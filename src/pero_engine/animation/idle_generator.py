"""Idle 애니메이션 생성기

캐릭터가 가만히 있을 때 자연스러운 움직임 생성:
- 눈 깜빡임 (랜덤 간격)
- 미세한 머리 흔들림
- 호흡 (가슴 움직임)
- 시선 이동
"""
import asyncio
import math
import random
import pickle
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass
class IdleConfig:
    """Idle 애니메이션 설정"""
    # 눈 깜빡임
    blink_interval_min: float = 2.0  # 최소 간격 (초)
    blink_interval_max: float = 6.0  # 최대 간격 (초)
    blink_duration: float = 0.15  # 깜빡임 지속 시간 (초)

    # 머리 움직임
    head_sway_amount: float = 0.02  # 흔들림 크기
    head_sway_speed: float = 0.3  # 흔들림 속도

    # 호흡
    breathing_amount: float = 0.03  # 호흡 크기
    breathing_speed: float = 0.4  # 호흡 속도 (Hz)

    # 시선
    gaze_change_interval: float = 3.0  # 시선 변경 간격
    gaze_range: float = 0.1  # 시선 범위

    # FPS
    fps: int = 30


class IdleGenerator:
    """Idle 애니메이션 생성기"""

    def __init__(self, config: Optional[IdleConfig] = None):
        self.config = config or IdleConfig()
        self._next_blink_time: float = 0.0
        self._next_gaze_time: float = 0.0
        self._current_gaze: Tuple[float, float] = (0.0, 0.0)

    def generate_idle_motion(
        self,
        duration: float,
        include_blink: bool = True,
        include_breathing: bool = True,
        include_head_sway: bool = True,
        include_gaze: bool = True,
    ) -> Dict:
        """
        Idle 모션 데이터 생성

        Args:
            duration: 생성할 애니메이션 길이 (초)
            include_blink: 눈 깜빡임 포함
            include_breathing: 호흡 포함
            include_head_sway: 머리 흔들림 포함
            include_gaze: 시선 이동 포함

        Returns:
            LivePortrait 호환 모션 데이터 딕셔너리
        """
        fps = self.config.fps
        num_frames = int(duration * fps)

        # 초기화
        motion_data = {
            'n_frames': num_frames,
            'fps': fps,
            # 눈 상태 (0=열림, 1=감김)
            'eye_close': np.zeros(num_frames, dtype=np.float32),
            # 머리 회전 (x=좌우, y=상하, z=기울기)
            'head_rotation': np.zeros((num_frames, 3), dtype=np.float32),
            # 호흡 (0~1)
            'breathing': np.zeros(num_frames, dtype=np.float32),
            # 시선 (x, y)
            'gaze': np.zeros((num_frames, 2), dtype=np.float32),
        }

        # 각 요소 생성
        if include_blink:
            self._generate_blinks(motion_data, duration)

        if include_breathing:
            self._generate_breathing(motion_data, duration)

        if include_head_sway:
            self._generate_head_sway(motion_data, duration)

        if include_gaze:
            self._generate_gaze(motion_data, duration)

        return motion_data

    def _generate_blinks(self, motion_data: Dict, duration: float):
        """눈 깜빡임 생성"""
        fps = self.config.fps
        num_frames = motion_data['n_frames']
        eye_close = motion_data['eye_close']

        current_time = 0.0
        blink_times = []

        # 깜빡임 시점 결정
        while current_time < duration:
            interval = random.uniform(
                self.config.blink_interval_min,
                self.config.blink_interval_max
            )
            current_time += interval
            if current_time < duration:
                blink_times.append(current_time)

        # 깜빡임 적용
        blink_frames = int(self.config.blink_duration * fps)
        half_blink = blink_frames // 2

        for blink_time in blink_times:
            center_frame = int(blink_time * fps)

            for i in range(-half_blink, half_blink + 1):
                frame_idx = center_frame + i
                if 0 <= frame_idx < num_frames:
                    # 부드러운 깜빡임 곡선 (코사인)
                    t = (i + half_blink) / blink_frames
                    eye_close[frame_idx] = math.sin(t * math.pi)

    def _generate_breathing(self, motion_data: Dict, duration: float):
        """호흡 생성"""
        fps = self.config.fps
        num_frames = motion_data['n_frames']
        breathing = motion_data['breathing']

        for i in range(num_frames):
            t = i / fps
            # 사인파로 호흡 시뮬레이션
            breathing[i] = (
                self.config.breathing_amount *
                (0.5 + 0.5 * math.sin(2 * math.pi * self.config.breathing_speed * t))
            )

    def _generate_head_sway(self, motion_data: Dict, duration: float):
        """머리 흔들림 생성"""
        fps = self.config.fps
        num_frames = motion_data['n_frames']
        head_rotation = motion_data['head_rotation']

        amount = self.config.head_sway_amount
        speed = self.config.head_sway_speed

        for i in range(num_frames):
            t = i / fps
            # 각 축에 대해 다른 주파수로 미세한 움직임
            head_rotation[i, 0] = amount * math.sin(speed * t * 2 * math.pi)  # 좌우
            head_rotation[i, 1] = amount * 0.5 * math.sin(speed * 0.7 * t * 2 * math.pi)  # 상하
            head_rotation[i, 2] = amount * 0.3 * math.sin(speed * 0.5 * t * 2 * math.pi)  # 기울기

    def _generate_gaze(self, motion_data: Dict, duration: float):
        """시선 이동 생성"""
        fps = self.config.fps
        num_frames = motion_data['n_frames']
        gaze = motion_data['gaze']

        interval = self.config.gaze_change_interval
        gaze_range = self.config.gaze_range

        current_gaze = np.array([0.0, 0.0])
        target_gaze = np.array([0.0, 0.0])
        change_frame = 0

        for i in range(num_frames):
            current_time = i / fps

            # 새 시선 타겟 설정
            if i >= change_frame:
                target_gaze = np.array([
                    random.uniform(-gaze_range, gaze_range),
                    random.uniform(-gaze_range, gaze_range),
                ])
                change_frame = i + int(interval * fps * random.uniform(0.8, 1.2))

            # 부드럽게 타겟으로 이동
            current_gaze += (target_gaze - current_gaze) * 0.1
            gaze[i] = current_gaze

    def save_motion_pkl(self, motion_data: Dict, output_path: str) -> bool:
        """모션 데이터를 PKL 파일로 저장"""
        try:
            # LivePortrait 호환 형식으로 변환
            lp_motion = self._convert_to_liveportrait_format(motion_data)

            with open(output_path, 'wb') as f:
                pickle.dump(lp_motion, f)

            return True
        except Exception as e:
            print(f"모션 PKL 저장 실패: {e}")
            return False

    def _convert_to_liveportrait_format(self, motion_data: Dict) -> Dict:
        """내부 모션 데이터를 LivePortrait 형식으로 변환"""
        num_frames = motion_data['n_frames']

        # LivePortrait에서 사용하는 키포인트 형식
        # 실제 형식은 LivePortrait 구현에 따라 조정 필요
        lp_data = {
            'n_frames': num_frames,
            'output_fps': motion_data['fps'],
            # 표현 파라미터 (예시 - 실제 구조 확인 필요)
            'exp': np.zeros((num_frames, 63), dtype=np.float32),
            # 포즈 (6DoF)
            'pose': np.zeros((num_frames, 6), dtype=np.float32),
            # 키포인트
            'kp': np.zeros((num_frames, 21, 3), dtype=np.float32),
        }

        # 머리 회전 적용
        lp_data['pose'][:, :3] = motion_data['head_rotation']

        # 눈 깜빡임을 표현 파라미터에 적용
        # (실제 인덱스는 LivePortrait 모델에 따라 다름)
        eye_close = motion_data['eye_close']
        lp_data['exp'][:, 0] = eye_close  # 왼쪽 눈
        lp_data['exp'][:, 1] = eye_close  # 오른쪽 눈

        return lp_data


class TalkingIdleGenerator(IdleGenerator):
    """말하는 중 Idle 애니메이션 생성기

    립싱크와 함께 사용할 보조 움직임 생성
    """

    def generate_talking_motion(
        self,
        duration: float,
        intensity: float = 1.0,
    ) -> Dict:
        """
        말하는 중 모션 생성 (립싱크 보조)

        Args:
            duration: 길이 (초)
            intensity: 움직임 강도 (0~2, 기본 1.0)

        Returns:
            모션 데이터
        """
        # 기본 idle에서 강도 조절
        original_head_sway = self.config.head_sway_amount
        original_breathing = self.config.breathing_amount

        self.config.head_sway_amount *= intensity * 1.5  # 말할 때 더 많이 움직임
        self.config.breathing_amount *= intensity * 0.8  # 호흡은 줄임

        motion_data = self.generate_idle_motion(
            duration,
            include_blink=True,
            include_breathing=True,
            include_head_sway=True,
            include_gaze=True,
        )

        # 설정 복원
        self.config.head_sway_amount = original_head_sway
        self.config.breathing_amount = original_breathing

        return motion_data


# 프리셋
class IdlePresets:
    """미리 정의된 Idle 설정들"""

    @staticmethod
    def calm() -> IdleConfig:
        """차분한 상태"""
        return IdleConfig(
            blink_interval_min=3.0,
            blink_interval_max=7.0,
            head_sway_amount=0.01,
            head_sway_speed=0.2,
            breathing_amount=0.02,
            breathing_speed=0.3,
        )

    @staticmethod
    def alert() -> IdleConfig:
        """활발한 상태"""
        return IdleConfig(
            blink_interval_min=1.5,
            blink_interval_max=4.0,
            head_sway_amount=0.03,
            head_sway_speed=0.5,
            breathing_amount=0.04,
            breathing_speed=0.5,
        )

    @staticmethod
    def sleepy() -> IdleConfig:
        """졸린 상태"""
        return IdleConfig(
            blink_interval_min=1.0,
            blink_interval_max=3.0,
            blink_duration=0.3,  # 느린 깜빡임
            head_sway_amount=0.02,
            head_sway_speed=0.15,
            breathing_amount=0.04,
            breathing_speed=0.25,
        )


async def test_idle_generator():
    """Idle 생성기 테스트"""
    print("🔍 Idle Generator 테스트...")

    generator = IdleGenerator(IdlePresets.calm())

    # 5초 idle 모션 생성
    motion_data = generator.generate_idle_motion(duration=5.0)

    print(f"✅ 모션 생성 완료")
    print(f"   프레임 수: {motion_data['n_frames']}")
    print(f"   눈 깜빡임 범위: {motion_data['eye_close'].min():.3f} ~ {motion_data['eye_close'].max():.3f}")
    print(f"   머리 움직임 범위: {motion_data['head_rotation'].min():.4f} ~ {motion_data['head_rotation'].max():.4f}")

    # PKL 저장 테스트
    output_path = "temp/test_idle.pkl"
    Path("temp").mkdir(exist_ok=True)

    if generator.save_motion_pkl(motion_data, output_path):
        print(f"✅ PKL 저장 완료: {output_path}")
    else:
        print("❌ PKL 저장 실패")


if __name__ == "__main__":
    asyncio.run(test_idle_generator())
