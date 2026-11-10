import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

import '../domain/user_record.dart';

class UserRepository {
  UserRepository({FirebaseDatabase? database})
    : _users = (database ?? FirebaseDatabase.instance).ref('users');

  final DatabaseReference _users;

  Stream<List<UserRecord>> watchUsers() {
    return _users.onValue.map((event) {
      final records = <UserRecord>[];
      for (final child in event.snapshot.children) {
        final value = child.value;
        if (value is Map<Object?, Object?> && child.key != null) {
          records.add(UserRecord.fromMap(child.key!, value));
        }
      }
      records.sort(
        (left, right) =>
            left.hoten.toLowerCase().compareTo(right.hoten.toLowerCase()),
      );
      return records;
    });
  }

  Future<bool> emailExists(String email, {String? exceptKey}) async {
    final normalizedEmail = email.trim().toLowerCase();
    final result = await _users
        .orderByChild('email')
        .equalTo(normalizedEmail)
        .get();

    return result.children.any((child) => child.key != exceptKey);
  }

  Future<void> create(UserRecord record) async {
    try {
      await _users.push().set(record.toMap());
    } on FirebaseException catch (error) {
      throw UserRepositoryFailure(_messageFor(error));
    }
  }

  Future<void> update(UserRecord record) async {
    if (record.key.isEmpty) {
      throw const UserRepositoryFailure('Không xác định được hồ sơ cần sửa.');
    }
    try {
      await _users.child(record.key).set(record.toMap());
    } on FirebaseException catch (error) {
      throw UserRepositoryFailure(_messageFor(error));
    }
  }

  Future<void> delete(String key) async {
    try {
      await _users.child(key).remove();
    } on FirebaseException catch (error) {
      throw UserRepositoryFailure(_messageFor(error));
    }
  }

  String _messageFor(FirebaseException error) {
    if (error.code == 'permission-denied') {
      return 'Phiên đăng nhập không có quyền thay đổi dữ liệu.';
    }
    if (error.code == 'network-error') {
      return 'Không thể kết nối Firebase. Kiểm tra mạng và thử lại.';
    }
    return 'Không thể lưu dữ liệu. Vui lòng thử lại.';
  }
}

class UserRepositoryFailure implements Exception {
  const UserRepositoryFailure(this.message);

  final String message;

  @override
  String toString() => message;
}
