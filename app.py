from datetime import datetime
from pathlib import Path
from typing import Any

import cv2


ROOT_DIR = Path(__file__).resolve().parent
ASSET_DIRS = {
	"photo": ROOT_DIR / "assets" / "photo",
	"video": ROOT_DIR / "assets" / "video",
}
RESULT_DIRS = {
	"photo": ROOT_DIR / "result" / "photo",
	"video": ROOT_DIR / "result" / "video",
}
SUPPORTED_EXTENSIONS = {
	"photo": {".jpg", ".jpeg", ".png", ".bmp", ".webp"},
	"video": {".mp4", ".avi", ".mov", ".mkv", ".m4v", ".webm"},
}
TARGET_CLASSES = {"person", "handbag", "cell phone"}
MODEL_NAME = "yolo11n.pt"
CONFIDENCE = 0.25


def list_media_files(media_type: str) -> list[Path]:
	folder = ASSET_DIRS[media_type]
	folder.mkdir(parents=True, exist_ok=True)
	return sorted(
		(
			path
			for path in folder.iterdir()
			if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS[media_type]
		),
		key=lambda path: path.name.casefold(),
	)


def choose_media_type() -> str | None:
	print("\nPilih jenis input:")
	print("1. Foto")
	print("2. Video")
	print("q. Keluar")
	choice = input("Pilihan: ").strip().lower()

	if choice == "1":
		return "photo"
	if choice == "2":
		return "video"
	if choice == "q":
		return None

	print("Pilihan tidak valid. Masukkan 1, 2, atau q.")
	return ""


def choose_file(files: list[Path]) -> tuple[int, Path] | None:
	print("\nDaftar file:")
	for index, path in enumerate(files, start=1):
		print(f"{index}. {path.name}")
	print("0. Kembali")

	choice = input("Pilih nomor file: ").strip()
	if choice == "0":
		return None
	if not choice.isdigit() or not 1 <= int(choice) <= len(files):
		print("Nomor file tidak valid.")
		return None

	index = int(choice)
	return index, files[index - 1]


def load_detector() -> tuple[Any, list[int]]:
	try:
		from ultralytics import YOLO
	except ImportError as error:
		raise RuntimeError(
			"Library belum terpasang."
		) from error

	print(f"Memuat model {MODEL_NAME}.")
	model = YOLO(MODEL_NAME)
	names = model.names
	if isinstance(names, dict):
		class_items = names.items()
	else:
		class_items = enumerate(names)

	class_ids = [
		class_id
		for class_id, name in class_items
		if str(name).strip().lower() in TARGET_CLASSES
	]
	if not class_ids:
		raise RuntimeError("Model tidak memiliki kelas person, handbag, atau cell phone.")
	return model, class_ids


def detect(model: Any, class_ids: list[int], frame: Any) -> Any:
	result = model.predict(
		source=frame,
		classes=class_ids,
		conf=CONFIDENCE,
		verbose=False,
	)[0]
	return result.plot()


def process_photo(model: Any, class_ids: list[int], source: Path, output: Path) -> None:
	image = cv2.imread(str(source))
	if image is None:
		raise RuntimeError(f"Foto tidak dapat dibaca: {source.name}")

	annotated_image = detect(model, class_ids, image)
	if not cv2.imwrite(str(output), annotated_image):
		raise RuntimeError(f"Hasil foto gagal disimpan: {output}")


def process_video(model: Any, class_ids: list[int], source: Path, output: Path) -> None:
	capture = cv2.VideoCapture(str(source))
	if not capture.isOpened():
		capture.release()
		raise RuntimeError(f"Video tidak dapat dibuka: {source.name}")

	writer = None
	frames_processed = 0
	try:
		has_frame, frame = capture.read()
		if not has_frame:
			raise RuntimeError(f"Video tidak memiliki frame yang dapat dibaca: {source.name}")

		fps = capture.get(cv2.CAP_PROP_FPS)
		if fps <= 0:
			fps = 30.0

		height, width = frame.shape[:2]
		fourcc = cv2.VideoWriter_fourcc(*"mp4v")
		writer = cv2.VideoWriter(str(output), fourcc, fps, (width, height))
		if not writer.isOpened():
			raise RuntimeError("Video hasil tidak dapat dibuat dengan codec mp4v.")

		total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
		while has_frame:
			writer.write(detect(model, class_ids, frame))
			frames_processed += 1

			if frames_processed % 100 == 0:
				if total_frames > 0:
					print(f"Memproses frame {frames_processed}/{total_frames}...")
				else:
					print(f"Memproses frame {frames_processed}...")
			has_frame, frame = capture.read()
	finally:
		capture.release()
		if writer is not None:
			writer.release()
 
	if frames_processed == 0:
		raise RuntimeError("Tidak ada frame video yang berhasil diproses.")


def main() -> None:
	detector = None
	class_ids = None

	print("YOLO-CAM: deteksi person, handbag, dan cell phone")
	while True:
		media_type = choose_media_type()
		if media_type is None:
			print("Selesai.")
			return
		if not media_type:
			continue

		files = list_media_files(media_type)
		if not files:
			print(f"Tidak ada file yang didukung di folder {ASSET_DIRS[media_type]}.")
			continue

		selection = choose_file(files)
		if selection is None:
			continue

		file_id, source = selection
		extension = ".png" if media_type == "photo" else ".mp4"
		date_stamp = datetime.now().strftime("%d%m%Y")
		output = RESULT_DIRS[media_type] / f"FX_C0{file_id}{date_stamp}{extension}"
		output.parent.mkdir(parents=True, exist_ok=True)

		if output.exists():
			print(f"Hasil sudah ada, tidak ditimpa: {output}")
			continue

		try:
			if detector is None or class_ids is None:
				detector, class_ids = load_detector()

			print(f"Memproses {source.name}...")
			if media_type == "photo":
				process_photo(detector, class_ids, source, output)
			else:
				process_video(detector, class_ids, source, output)
			print(f"Selesai. Hasil tersimpan di: {output}")
		except Exception as error:
			print(f"Gagal memproses file: {error}")


if __name__ == "__main__":
	try:
		main()
	except (KeyboardInterrupt, EOFError):
		print("\nProgram dihentikan.")