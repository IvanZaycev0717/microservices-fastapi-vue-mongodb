import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent.parent
    proto_dir = project_root / "src/protos"
    output_dir = project_root / "src/protos"

    output_dir.mkdir(parents=True, exist_ok=True)

    proto_files = list(proto_dir.glob("*.proto"))

    if not proto_files:
        print("❌ No .proto files found")
        sys.exit(1)

    python_executable = sys.executable

    for proto_file in proto_files:
        cmd = [
            python_executable,
            "-m",
            "grpc_tools.protoc",
            f"-I{proto_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            f"--pyi_out={output_dir}",
            str(proto_file),
        ]

        print(f"Running: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True, cwd=project_root)
            print(f"✅ {proto_file.name} успешно сгенерирован")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка генерации {proto_file.name}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
