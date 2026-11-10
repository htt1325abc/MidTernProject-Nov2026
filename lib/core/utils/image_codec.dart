import 'dart:convert';
import 'dart:typed_data';

import 'package:image/image.dart' as img;
import 'package:image_picker/image_picker.dart';

abstract final class ImageCodecService {
  static const int maxDimension = 720;
  static const int jpegQuality = 72;

  static Future<String?> pickCompressedImage() async {
    final file = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (file == null) {
      return null;
    }

    final bytes = await file.readAsBytes();
    return compressToBase64(bytes);
  }

  static String compressToBase64(Uint8List bytes) {
    final decoded = img.decodeImage(bytes);
    if (decoded == null) {
      throw const FormatException('Tệp được chọn không phải là ảnh hợp lệ.');
    }

    final longestSide = decoded.width > decoded.height
        ? decoded.width
        : decoded.height;
    final resized = longestSide > maxDimension
        ? decoded.width >= decoded.height
              ? img.copyResize(decoded, width: maxDimension)
              : img.copyResize(decoded, height: maxDimension)
        : decoded;

    final encoded = img.encodeJpg(resized, quality: jpegQuality);
    return base64Encode(encoded);
  }

  static Uint8List decode(String value) => base64Decode(value);
}
