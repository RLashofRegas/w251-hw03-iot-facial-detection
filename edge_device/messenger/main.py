"""Entrypoint for the face detection package for the edge_device."""
import argparse
from uuid import uuid4
from face_detection.face_detector import FaceDetector, IFaceDetector
from face_detection.neural_face_detector import NeuralFaceDetector
from face_detection.video_streamer import VideoStreamer
from face_detection.messaging_client import FaceMessenger
import os


class FaceDetectionRunner:
    """The runner of the face detection pipeline."""

    def __init__(
            self,
            output_channel: str,
            broker_host: str,
            broker_port: int,
            video_input: int,
            guarantee_level: int,
            face_detector: IFaceDetector) -> None:
        """Initialize the runner.

        Args:
            output_channel: the channel to output messages to.
            broker_host: hostname of the message broker.
            broker_port: port of the message broker.
            video_input: input index of the video camera
                (e.g. 0 for /dev/video0)
            guarantee_level: level of guarantee for message delivery.
                0 = at most once, 1 = at least once, 2 = exactly once.
        """
        video_streamer = VideoStreamer(face_detector, video_input)
        self.messenger = FaceMessenger(
            output_channel,
            broker_host,
            broker_port,
            video_streamer,
            guarantee_level=guarantee_level)

    def run(self) -> None:
        """Run the face detection pipeline."""
        self.messenger.stream_messages()


if(__name__ == "__main__"):
    devices = os.listdir('/dev')
    print(devices)
    client_id = uuid4()
    print(f'Face detection client started for client_id={client_id}')
    arg_parser = argparse.ArgumentParser(
        description="Run the face detection pipeline.")
    arg_parser.add_argument(
        '-c', '--channel', type=str, default=f'faces/{client_id}',
        help='Output channel to be used for publishing messages.')
    arg_parser.add_argument(
        '-b', '--broker', type=str, required=True,
        help='Hostname of the message broker.')
    arg_parser.add_argument(
        '-p', '--port', type=int, required=True,
        help='Port on the broker host to publish messages to.')
    arg_parser.add_argument(
        '-v', '--video', type=int, default=0,
        help='Video input for the video camera (e.g. 0 for /dev/video0)')
    arg_parser.add_argument(
        '-g', '--guarantee', type=int, default=0,
        help='Level of guarantee for message delivery.')
    arg_parser.add_argument(
        '-d', '--detector', type=str, default=f'neural',
        help='Whether to use opencv or neural face detector')
    arg_parser.add_argument(
        '-f', '--detector_path', type=str,
        help='Path to detector saved graph.')
    arg_parser.add_argument(
        '-w', '--width', type=str,
        help='Input image width for detector.')
    arg_parser.add_argument(
        '-h', '--height', type=str,
        help='Input image height for detector.')
    args = arg_parser.parse_args()
    face_detector: IFaceDetector
    if (args.detector == 'neural'):
        assert args.detector_path is not None
        assert args.width is not None
        assert args.height is not None
        face_detector = NeuralFaceDetector(
            args.detector_path, (args.width, args.height))
    else:
        if (args.detector_path is not None):
            face_detector = FaceDetector(args.detector_path)
        else:
            face_detector = FaceDetector()

    runner = FaceDetectionRunner(
        args.channel,
        args.broker,
        args.port,
        args.video,
        args.guarantee,
        face_detector)
    runner.run()
