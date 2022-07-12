from dataclasses import asdict, dataclass


@dataclass
class Unsupported:
    fname: str

    def __str__(self):
        return f"Unsupported format for {self.fname}"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
