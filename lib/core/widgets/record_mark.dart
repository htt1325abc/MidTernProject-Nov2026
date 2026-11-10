import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class RecordMark extends StatelessWidget {
  const RecordMark({this.compact = false, super.key});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: compact ? 34 : 42,
          height: compact ? 34 : 42,
          decoration: BoxDecoration(
            color: AppColors.ink,
            borderRadius: BorderRadius.circular(10),
          ),
          alignment: Alignment.center,
          child: Text(
            'U/',
            style: TextStyle(
              color: AppColors.mint,
              fontSize: compact ? 14 : 17,
              fontWeight: FontWeight.w900,
              letterSpacing: -1,
            ),
          ),
        ),
        const SizedBox(width: 10),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'USER REGISTRY',
              style: TextStyle(
                color: AppColors.ink,
                fontSize: compact ? 12 : 14,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.2,
              ),
            ),
            if (!compact)
              const Text(
                'ADMIN CONSOLE · 2026',
                style: TextStyle(
                  color: AppColors.inkMuted,
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1,
                ),
              ),
          ],
        ),
      ],
    );
  }
}
