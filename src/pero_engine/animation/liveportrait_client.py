"""LivePortrait 애니메이션 클라이언트

FasterLivePortrait + JoyVASA를 사용하여 오디오 기반 립싱크 애니메이션 생성
"""
import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from .base import BaseAnimation


class LivePortraitClient(BaseAnimation):
    """LivePortrait + JoyVASA 기반 애니메이션 클라이언트

    두 가지 모드 지원:
    1. Audio-driven (JoyVASA): 오디오 → 자동 립싱크 + 머리 움직임
    2. Template-driven: 미리 만든 모션 템플릿 (.pkl) 사용
    """

    def __init__(
        self,
        liveportrait_path: Optional[str] = None,
        joyvasa_path: Optional[str] = None,
        device: str = "auto",
        fps: int = 30,
        use_tensorrt: bool = True,
        backend: str = "joyvasa",  # joyvasa, template
    ):
        """
        Args:
            liveportrait_path: FasterLivePortrait 설치 경로
            joyvasa_path: JoyVASA 설치 경로
            device: 'auto', 'cpu', 'cuda'
            fps: 출력 비디오 FPS
            use_tensorrt: TensorRT 최적화 사용 여부
            backend: 'joyvasa' (오디오 드리븐) 또는 'template' (모션 템플릿)
        """
        self.liveportrait_path = liveportrait_path or os.getenv(
            "LIVEPORTRAIT_PATH",
            str(Path.home() / "FasterLivePortrait")
        )
        self.joyvasa_path = joyvasa_path or os.getenv(
            "JOYVASA_PATH",
            str(Path.home() / "JoyVASA")
        )
        self.device = self._resolve_device(device)
        self.fps = fps
        self.use_tensorrt = use_tensorrt
        self.backend = backend
        self.initialized = False

        # 캐시된 소스 이미지 정보 (동일 이미지 재사용 최적화)
        self._cached_source: Optional[str] = None
        self._cached_source_features: Optional[Any] = None

    def _resolve_device(self, device: str) -> str:
        """디바이스 자동 감지"""
        if device == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    async def is_available(self) -> bool:
        """LivePortrait/JoyVASA 사용 가능 여부 확인"""
        # FasterLivePortrait 확인
        lp_available = await self._check_liveportrait()

        # JoyVASA 확인 (joyvasa 백엔드일 때만)
        if self.backend == "joyvasa":
            jv_available = await self._check_joyvasa()
            return lp_available and jv_available

        return lp_available

    async def _check_liveportrait(self) -> bool:
        """FasterLivePortrait 설치 확인"""
        lp_path = Path(self.liveportrait_path)

        if not lp_path.exists():
            print(f"⚠️  FasterLivePortrait를 찾을 수 없습니다: {self.liveportrait_path}")
            print("   설치: git clone https://github.com/warmshao/FasterLivePortrait")
            return False

        # run.py 또는 inference.py 확인
        run_script = lp_path / "run.py"
        if not run_script.exists():
            print(f"⚠️  FasterLivePortrait run.py를 찾을 수 없습니다")
            return False

        print(f"✅ FasterLivePortrait 확인됨: {self.liveportrait_path}")
        return True

    async def _check_joyvasa(self) -> bool:
        """JoyVASA 설치 확인"""
        jv_path = Path(self.joyvasa_path)

        if not jv_path.exists():
            print(f"⚠️  JoyVASA를 찾을 수 없습니다: {self.joyvasa_path}")
            print("   설치: git clone https://github.com/jdh-algo/JoyVASA")
            return False

        print(f"✅ JoyVASA 확인됨: {self.joyvasa_path}")
        return True

    async def generate(
        self,
        image_path: str,
        audio_path: str,
        output_path: str,
    ) -> bool:
        """
        이미지 + 오디오 → 립싱크 비디오 생성

        Args:
            image_path: 캐릭터 이미지 경로
            audio_path: 오디오 파일 경로 (wav, mp3)
            output_path: 출력 비디오 경로 (.mp4)

        Returns:
            성공 여부
        """
        # 파일 존재 확인
        if not Path(image_path).exists():
            print(f"❌ 이미지를 찾을 수 없습니다: {image_path}")
            return False

        if not Path(audio_path).exists():
            print(f"❌ 오디오를 찾을 수 없습니다: {audio_path}")
            return False

        print(f"🎬 LivePortrait 애니메이션 생성 시작...")
        print(f"   이미지: {image_path}")
        print(f"   오디오: {audio_path}")
        print(f"   출력: {output_path}")
        print(f"   백엔드: {self.backend}")

        try:
            if self.backend == "joyvasa":
                return await self._generate_with_joyvasa(
                    image_path, audio_path, output_path
                )
            else:
                return await self._generate_with_template(
                    image_path, audio_path, output_path
                )
        except Exception as e:
            print(f"❌ 애니메이션 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def _generate_with_joyvasa(
        self,
        image_path: str,
        audio_path: str,
        output_path: str,
    ) -> bool:
        """JoyVASA를 사용한 오디오 드리븐 애니메이션 생성"""

        # Step 1: JoyVASA로 오디오 → 모션 템플릿 생성
        print("   [1/2] JoyVASA: 오디오 → 모션 생성 중...")

        motion_pkl_path = Path(output_path).with_suffix('.pkl')

        joyvasa_success = await self._run_joyvasa(
            image_path=image_path,
            audio_path=audio_path,
            output_pkl=str(motion_pkl_path),
        )

        if not joyvasa_success:
            print("❌ JoyVASA 모션 생성 실패")
            return False

        # Step 2: FasterLivePortrait로 이미지 + 모션 → 비디오
        print("   [2/2] LivePortrait: 이미지 + 모션 → 비디오 생성 중...")

        lp_success = await self._run_liveportrait(
            image_path=image_path,
            driving_path=str(motion_pkl_path),
            output_path=output_path,
        )

        # 임시 pkl 파일 정리
        if motion_pkl_path.exists():
            motion_pkl_path.unlink()

        if lp_success:
            print(f"✅ 애니메이션 생성 완료: {output_path}")

        return lp_success

    async def _generate_with_template(
        self,
        image_path: str,
        audio_path: str,
        output_path: str,
        template_path: Optional[str] = None,
    ) -> bool:
        """모션 템플릿을 사용한 애니메이션 생성 (립싱크는 별도 처리 필요)"""

        # 기본 템플릿 경로
        if template_path is None:
            template_path = str(
                Path(self.liveportrait_path) / "assets/examples/driving/d0.mp4"
            )

        return await self._run_liveportrait(
            image_path=image_path,
            driving_path=template_path,
            output_path=output_path,
            audio_path=audio_path,  # 오디오 합성용
        )

    async def _run_joyvasa(
        self,
        image_path: str,
        audio_path: str,
        output_pkl: str,
    ) -> bool:
        """JoyVASA 실행: 오디오 → 모션 템플릿 (.pkl)"""

        jv_path = Path(self.joyvasa_path)
        inference_script = jv_path / "inference.py"

        if not inference_script.exists():
            print(f"⚠️  JoyVASA inference.py를 찾을 수 없습니다")
            # Fallback: 더미 모션 생성
            return await self._generate_dummy_motion(output_pkl)

        cmd = [
            "python", str(inference_script),
            "--source_image", image_path,
            "--audio_path", audio_path,
            "--output_path", output_pkl,
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(jv_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                print(f"JoyVASA 오류: {stderr.decode()}")
                return await self._generate_dummy_motion(output_pkl)

            return Path(output_pkl).exists()

        except Exception as e:
            print(f"JoyVASA 실행 실패: {e}")
            return await self._generate_dummy_motion(output_pkl)

    async def _run_liveportrait(
        self,
        image_path: str,
        driving_path: str,
        output_path: str,
        audio_path: Optional[str] = None,
    ) -> bool:
        """FasterLivePortrait 실행: 이미지 + 드라이빙 → 비디오"""

        lp_path = Path(self.liveportrait_path)
        run_script = lp_path / "run.py"

        if not run_script.exists():
            print(f"⚠️  FasterLivePortrait를 사용할 수 없습니다")
            # Fallback: 정적 이미지 + 오디오로 더미 비디오 생성
            return await self._generate_dummy_video(
                image_path, audio_path, output_path
            )

        # TensorRT 또는 ONNX 설정
        config_file = "configs/trt_infer.yaml" if self.use_tensorrt else "configs/onnx_infer.yaml"

        cmd = [
            "python", str(run_script),
            "--src_image", image_path,
            "--dri_video", driving_path,
            "--output", output_path,
            "--cfg", config_file,
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(lp_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                print(f"LivePortrait 오류: {stderr.decode()}")
                return await self._generate_dummy_video(
                    image_path, audio_path, output_path
                )

            # 오디오 합성 (필요시)
            if audio_path and Path(output_path).exists():
                await self._merge_audio(output_path, audio_path)

            return Path(output_path).exists()

        except Exception as e:
            print(f"LivePortrait 실행 실패: {e}")
            return await self._generate_dummy_video(
                image_path, audio_path, output_path
            )

    async def _generate_dummy_motion(self, output_pkl: str) -> bool:
        """더미 모션 데이터 생성 (테스트/폴백용)"""
        import pickle
        import numpy as np

        # 간단한 idle 모션 데이터
        # 실제로는 눈 깜빡임, 미세한 움직임 등을 포함
        num_frames = 75  # 약 2.5초 @ 30fps

        motion_data = {
            'n_frames': num_frames,
            # 3D keypoints (21 points * 3 coords)
            'keypoints': np.zeros((num_frames, 21, 3), dtype=np.float32),
            # 표정 파라미터
            'exp': np.zeros((num_frames, 63), dtype=np.float32),
            # 머리 포즈 (rotation + translation)
            'pose': np.zeros((num_frames, 6), dtype=np.float32),
        }

        # 간단한 눈 깜빡임 시뮬레이션 (프레임 30-35에서)
        # 실제 구현에서는 더 자연스러운 모션 필요

        try:
            with open(output_pkl, 'wb') as f:
                pickle.dump(motion_data, f)
            return True
        except Exception as e:
            print(f"더미 모션 생성 실패: {e}")
            return False

    async def _generate_dummy_video(
        self,
        image_path: str,
        audio_path: Optional[str],
        output_path: str,
    ) -> bool:
        """더미 비디오 생성 (정적 이미지 + 오디오)"""
        try:
            import subprocess

            # ffmpeg로 정적 이미지 + 오디오 → 비디오
            if audio_path and Path(audio_path).exists():
                # 오디오 길이 구하기
                cmd_duration = [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    audio_path
                ]
                result = subprocess.run(cmd_duration, capture_output=True, text=True)
                duration = float(result.stdout.strip()) if result.stdout.strip() else 3.0

                # 이미지 + 오디오 → 비디오
                cmd = [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", image_path,
                    "-i", audio_path,
                    "-c:v", "libx264",
                    "-tune", "stillimage",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    "-t", str(duration),
                    output_path
                ]
            else:
                # 오디오 없이 3초 비디오
                cmd = [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", image_path,
                    "-c:v", "libx264",
                    "-t", "3",
                    "-pix_fmt", "yuv420p",
                    output_path
                ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            if Path(output_path).exists():
                print(f"⚠️  더미 비디오 생성됨 (정적 이미지): {output_path}")
                return True
            return False

        except Exception as e:
            print(f"더미 비디오 생성 실패: {e}")
            return False

    async def _merge_audio(self, video_path: str, audio_path: str) -> bool:
        """비디오에 오디오 합성"""
        try:
            output_temp = video_path + ".temp.mp4"

            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                output_temp
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            if Path(output_temp).exists():
                Path(video_path).unlink()
                Path(output_temp).rename(video_path)
                return True
            return False

        except Exception as e:
            print(f"오디오 합성 실패: {e}")
            return False

    async def generate_idle(
        self,
        image_path: str,
        output_path: str,
        duration: float = 3.0,
    ) -> bool:
        """Idle 애니메이션 생성 (눈 깜빡임, 미세한 움직임)"""

        # Idle 모션 템플릿 경로
        idle_template = Path(self.liveportrait_path) / "assets/examples/driving/idle.pkl"

        if idle_template.exists():
            return await self._run_liveportrait(
                image_path=image_path,
                driving_path=str(idle_template),
                output_path=output_path,
            )
        else:
            # 더미 idle 비디오 생성
            return await self._generate_dummy_video(
                image_path, None, output_path
            )


# 테스트
async def test_liveportrait():
    """LivePortrait 테스트"""
    print("🔍 LivePortrait 테스트 시작...")

    client = LivePortraitClient(
        device="auto",
        fps=30,
        backend="joyvasa",
    )

    available = await client.is_available()
    if not available:
        print("⚠️  LivePortrait/JoyVASA가 설치되지 않았습니다.")
        print("   더미 비디오 생성 모드로 동작합니다.")

    # 테스트 파일
    image_path = "static/pero_sample_img.png"
    audio_path = "temp/test_audio.mp3"
    output_path = "temp/test_output.mp4"

    if Path(image_path).exists() and Path(audio_path).exists():
        success = await client.generate(image_path, audio_path, output_path)
        print(f"결과: {'성공' if success else '실패'}")
    else:
        print("테스트 파일이 없습니다.")


if __name__ == "__main__":
    asyncio.run(test_liveportrait())
