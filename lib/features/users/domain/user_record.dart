class UserRecord {
  const UserRecord({
    required this.key,
    required this.email,
    required this.matkhau,
    required this.hoten,
    required this.hinhanh,
  });

  /// Firebase node key. This is never serialized as a database field.
  final String key;
  final String email;
  final String matkhau;
  final String hoten;
  final String hinhanh;

  factory UserRecord.fromMap(String key, Map<Object?, Object?> map) {
    return UserRecord(
      key: key,
      email: map['email']?.toString() ?? '',
      matkhau: map['matkhau']?.toString() ?? '',
      hoten: map['hoten']?.toString() ?? '',
      hinhanh: map['hinhanh']?.toString() ?? '',
    );
  }

  /// The assignment accepts exactly these four database fields.
  Map<String, String> toMap() => {
    'email': email,
    'matkhau': matkhau,
    'hoten': hoten,
    'hinhanh': hinhanh,
  };

  UserRecord copyWith({
    String? key,
    String? email,
    String? matkhau,
    String? hoten,
    String? hinhanh,
  }) {
    return UserRecord(
      key: key ?? this.key,
      email: email ?? this.email,
      matkhau: matkhau ?? this.matkhau,
      hoten: hoten ?? this.hoten,
      hinhanh: hinhanh ?? this.hinhanh,
    );
  }
}
