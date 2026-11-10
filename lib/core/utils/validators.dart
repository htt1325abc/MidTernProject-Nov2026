abstract final class Validators {
  static final RegExp _emailPattern = RegExp(
    r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
  );

  static String? requiredText(String? value, String label) {
    if (value == null || value.trim().isEmpty) {
      return 'Vui lòng nhập $label.';
    }
    return null;
  }

  static String? email(String? value) {
    final requiredError = requiredText(value, 'email');
    if (requiredError != null) {
      return requiredError;
    }
    if (!_emailPattern.hasMatch(value!.trim())) {
      return 'Email chưa đúng định dạng.';
    }
    return null;
  }

  static String? password(String? value) {
    final requiredError = requiredText(value, 'mật khẩu');
    if (requiredError != null) {
      return requiredError;
    }
    if (value!.length < 6) {
      return 'Mật khẩu cần ít nhất 6 ký tự.';
    }
    return null;
  }
}
