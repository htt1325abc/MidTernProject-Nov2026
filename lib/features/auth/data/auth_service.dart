import 'package:firebase_auth/firebase_auth.dart';

class AuthService {
  AuthService({FirebaseAuth? firebaseAuth})
    : _firebaseAuth = firebaseAuth ?? FirebaseAuth.instance;

  final FirebaseAuth _firebaseAuth;

  Stream<User?> get authStateChanges => _firebaseAuth.authStateChanges();

  Future<void> signIn({required String email, required String password}) async {
    try {
      await _firebaseAuth.signInWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );
    } on FirebaseAuthException catch (error) {
      throw AuthFailure(_messageFor(error.code));
    }
  }

  Future<void> signOut() => _firebaseAuth.signOut();

  String _messageFor(String code) {
    return switch (code) {
      'invalid-email' => 'Email quản trị chưa đúng định dạng.',
      'user-disabled' => 'Tài khoản quản trị đã bị vô hiệu hóa.',
      'user-not-found' ||
      'wrong-password' ||
      'invalid-credential' => 'Email hoặc mật khẩu không đúng.',
      'too-many-requests' => 'Đăng nhập quá nhiều lần. Vui lòng thử lại sau.',
      _ => 'Không thể đăng nhập. Kiểm tra kết nối và thử lại.',
    };
  }
}

class AuthFailure implements Exception {
  const AuthFailure(this.message);

  final String message;

  @override
  String toString() => message;
}
