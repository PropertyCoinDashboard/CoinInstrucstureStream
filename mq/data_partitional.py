from kafka.partitioner.default import DefaultPartitioner, murmur2

from typing import Optional
import random


class CoinHashingCustomPartitional(DefaultPartitioner):
    """가상화폐 특정 파티션"""

    @classmethod
    def __call__(
        cls, key: Optional[str], all_partitions: list[int], available: list[int]
    ) -> int:
        """
        Args:
            key (Optional[str]): 파티션에 사용할 키 (가상화폐 이름 등)
            all_partitions (List[int]): 모든 파티션 ID 리스트
            available (List[int]): 사용 가능한 파티션 ID 리스트

        Returns:
            int: 선택된 파티션 ID
        """
        try:
            if key is not None:
                if isinstance(key, str):
                    key = key.encode("utf-8")  # 문자열을 bytes로 변환
                # 키 해싱 하여 파티션 선택
                hashed_key: int = murmur2(key)
                hashed_key &= 0x7FFFFFF

                # hash(key) % 파티션 개수
                partition_idx: int = hashed_key % len(all_partitions)
                print(f"{key} --> {partition_idx}")
                return all_partitions[partition_idx]  # 해싱된 값이 따라서 파티션 적재

            return super(CoinHashingCustomPartitional, cls).__call__(
                key=key, all_partitions=all_partitions, available=available
            )
        except Exception as e:
            print(f"파티션 오류 {key}: {e}")
            return random.choice(all_partitions)
