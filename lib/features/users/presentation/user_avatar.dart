import 'package:flutter/material.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/utils/image_codec.dart';

class UserAvatar extends StatelessWidget {
  const UserAvatar({
    required this.imageData,
    this.size = 48,
    this.borderRadius,
    super.key,
  });

  final String imageData;
  final double size;
  final BorderRadius? borderRadius;

  @override
  Widget build(BuildContext context) {
    final radius = borderRadius ?? BorderRadius.circular(size * 0.28);

    Widget image;
    try {
      image = Image.memory(
        ImageCodecService.decode(imageData),
        width: size,
        height: size,
        fit: BoxFit.cover,
        gaplessPlayback: true,
        errorBuilder: (_, _, _) => _fallback(),
      );
    } on FormatException {
      image = _fallback();
    }

    return ClipRRect(borderRadius: radius, child: image);
  }

  Widget _fallback() {
    return Container(
      width: size,
      height: size,
      color: AppColors.line,
      alignment: Alignment.center,
      child: Icon(
        Icons.person_outline_rounded,
        color: AppColors.inkMuted,
        size: size * 0.48,
      ),
    );
  }
}
