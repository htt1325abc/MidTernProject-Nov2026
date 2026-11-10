import 'package:flutter_test/flutter_test.dart';
import 'package:midtern_project/core/utils/validators.dart';

void main() {
  group('Validators', () {
    test('accepts a valid email and rejects malformed input', () {
      expect(Validators.email('admin@example.com'), isNull);
      expect(Validators.email('not-an-email'), isNotNull);
    });

    test('requires a password of at least six characters', () {
      expect(Validators.password('123456'), isNull);
      expect(Validators.password('12345'), isNotNull);
    });

    test('requires a full name', () {
      expect(Validators.requiredText('Nguyễn Thị Lan', 'họ tên'), isNull);
      expect(Validators.requiredText('', 'họ tên'), isNotNull);
    });
  });
}
