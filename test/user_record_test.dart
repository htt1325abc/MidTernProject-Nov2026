import 'package:flutter_test/flutter_test.dart';
import 'package:midtern_project/features/users/domain/user_record.dart';

void main() {
  group('UserRecord', () {
    test('serializes exactly the four fields required by the assignment', () {
      const record = UserRecord(
        key: 'firebase-runtime-key',
        email: 'lan@example.com',
        matkhau: 'Secret123',
        hoten: 'Nguyễn Thị Lan',
        hinhanh: 'data:image/jpeg;base64,abc',
      );

      final map = record.toMap();

      expect(
        map.keys,
        unorderedEquals(['email', 'matkhau', 'hoten', 'hinhanh']),
      );
      expect(map, hasLength(4));
      expect(map, isNot(contains('key')));
    });

    test('reads a Firebase map and keeps its node key at runtime only', () {
      final record = UserRecord.fromMap('node-01', {
        'email': 'minh@example.com',
        'matkhau': 'Password1',
        'hoten': 'Trần Văn Minh',
        'hinhanh': '',
      });

      expect(record.key, 'node-01');
      expect(record.hoten, 'Trần Văn Minh');
      expect(record.toMap(), isNot(contains('key')));
    });
  });
}
