import 'package:flutter/material.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/utils/image_codec.dart';
import '../../../core/utils/validators.dart';
import '../data/user_repository.dart';
import '../domain/user_record.dart';
import 'user_avatar.dart';

Future<bool?> showUserFormDialog(
  BuildContext context, {
  required UserRepository repository,
  UserRecord? existing,
}) {
  return showDialog<bool>(
    context: context,
    barrierDismissible: false,
    builder: (_) => UserFormDialog(repository: repository, existing: existing),
  );
}

class UserFormDialog extends StatefulWidget {
  const UserFormDialog({required this.repository, this.existing, super.key});

  final UserRepository repository;
  final UserRecord? existing;

  @override
  State<UserFormDialog> createState() => _UserFormDialogState();
}

class _UserFormDialogState extends State<UserFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _emailController;
  late final TextEditingController _passwordController;
  String _imageData = '';
  bool _obscurePassword = true;
  bool _isPickingImage = false;
  bool _isSaving = false;
  String? _errorMessage;

  bool get _isEditing => widget.existing != null;

  @override
  void initState() {
    super.initState();
    final existing = widget.existing;
    _nameController = TextEditingController(text: existing?.hoten ?? '');
    _emailController = TextEditingController(text: existing?.email ?? '');
    _passwordController = TextEditingController(text: existing?.matkhau ?? '');
    _imageData = existing?.hinhanh ?? '';
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _pickImage() async {
    setState(() {
      _isPickingImage = true;
      _errorMessage = null;
    });
    try {
      final result = await ImageCodecService.pickCompressedImage();
      if (result != null && mounted) {
        setState(() => _imageData = result);
      }
    } on FormatException catch (error) {
      if (mounted) {
        setState(() => _errorMessage = error.message);
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => _errorMessage = 'Không thể đọc ảnh. Vui lòng chọn ảnh khác.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isPickingImage = false);
      }
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    if (_imageData.isEmpty) {
      setState(() => _errorMessage = 'Vui lòng chọn hình ảnh người dùng.');
      return;
    }

    setState(() {
      _isSaving = true;
      _errorMessage = null;
    });

    final email = _emailController.text.trim().toLowerCase();
    try {
      final duplicate = await widget.repository.emailExists(
        email,
        exceptKey: widget.existing?.key,
      );
      if (duplicate) {
        if (mounted) {
          setState(
            () => _errorMessage = 'Email này đã tồn tại trong hệ thống.',
          );
        }
        return;
      }

      final record = UserRecord(
        key: widget.existing?.key ?? '',
        email: email,
        matkhau: _passwordController.text,
        hoten: _nameController.text.trim(),
        hinhanh: _imageData,
      );

      if (_isEditing) {
        await widget.repository.update(record);
      } else {
        await widget.repository.create(record);
      }

      if (mounted) {
        Navigator.of(context).pop(true);
      }
    } on UserRepositoryFailure catch (error) {
      if (mounted) {
        setState(() => _errorMessage = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final mediaQuery = MediaQuery.of(context);
    final isCompact = mediaQuery.size.width < 620;

    return Dialog(
      insetPadding: EdgeInsets.all(isCompact ? 12 : 28),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      clipBehavior: Clip.antiAlias,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: 720,
          maxHeight: mediaQuery.size.height - (isCompact ? 24 : 56),
        ),
        child: Column(
          children: [
            Container(
              color: AppColors.ink,
              padding: const EdgeInsets.fromLTRB(24, 20, 16, 20),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _isEditing ? 'CHỈNH SỬA HỒ SƠ' : 'TẠO HỒ SƠ MỚI',
                          style: const TextStyle(
                            color: AppColors.mint,
                            fontSize: 11,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 1.4,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _isEditing
                              ? 'Cập nhật người dùng'
                              : 'Thêm người dùng',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 23,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: _isSaving ? null : () => Navigator.pop(context),
                    tooltip: 'Đóng',
                    color: Colors.white,
                    icon: const Icon(Icons.close_rounded),
                  ),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _ImagePickerField(
                        imageData: _imageData,
                        isLoading: _isPickingImage,
                        onPressed: _isSaving ? null : _pickImage,
                      ),
                      const SizedBox(height: 24),
                      TextFormField(
                        controller: _nameController,
                        validator: (value) =>
                            Validators.requiredText(value, 'họ tên'),
                        textCapitalization: TextCapitalization.words,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          labelText: 'Họ tên',
                          prefixIcon: Icon(Icons.badge_outlined),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _emailController,
                        validator: Validators.email,
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          labelText: 'Email',
                          prefixIcon: Icon(Icons.alternate_email_rounded),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _passwordController,
                        validator: Validators.password,
                        obscureText: _obscurePassword,
                        onFieldSubmitted: (_) => _save(),
                        decoration: InputDecoration(
                          labelText: 'Mật khẩu',
                          prefixIcon: const Icon(Icons.key_rounded),
                          suffixIcon: IconButton(
                            onPressed: () => setState(
                              () => _obscurePassword = !_obscurePassword,
                            ),
                            tooltip: _obscurePassword
                                ? 'Hiện mật khẩu'
                                : 'Ẩn mật khẩu',
                            icon: Icon(
                              _obscurePassword
                                  ? Icons.visibility_outlined
                                  : Icons.visibility_off_outlined,
                            ),
                          ),
                        ),
                      ),
                      if (_errorMessage != null) ...[
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: AppColors.coral.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(
                              color: Color(0xFFB42318),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                      const SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton(
                            onPressed: _isSaving
                                ? null
                                : () => Navigator.pop(context),
                            child: const Text('Hủy'),
                          ),
                          const SizedBox(width: 12),
                          FilledButton.icon(
                            onPressed: _isSaving ? null : _save,
                            icon: _isSaving
                                ? const SizedBox.square(
                                    dimension: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Icon(Icons.save_outlined),
                            label: Text(
                              _isSaving
                                  ? 'Đang lưu...'
                                  : _isEditing
                                  ? 'Lưu thay đổi'
                                  : 'Thêm người dùng',
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ImagePickerField extends StatelessWidget {
  const _ImagePickerField({
    required this.imageData,
    required this.isLoading,
    required this.onPressed,
  });

  final String imageData;
  final bool isLoading;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        if (imageData.isEmpty)
          Container(
            width: 92,
            height: 92,
            decoration: BoxDecoration(
              color: AppColors.canvas,
              borderRadius: BorderRadius.circular(22),
              border: Border.all(color: AppColors.line),
            ),
            child: const Icon(
              Icons.add_photo_alternate_outlined,
              color: AppColors.inkMuted,
              size: 34,
            ),
          )
        else
          UserAvatar(
            imageData: imageData,
            size: 92,
            borderRadius: BorderRadius.circular(22),
          ),
        const SizedBox(width: 18),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Hình ảnh',
                style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
              ),
              const SizedBox(height: 4),
              const Text(
                'Ảnh được nén trước khi lưu vào Firebase.',
                style: TextStyle(color: AppColors.inkMuted),
              ),
              const SizedBox(height: 10),
              OutlinedButton.icon(
                onPressed: isLoading ? null : onPressed,
                icon: isLoading
                    ? const SizedBox.square(
                        dimension: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.photo_library_outlined),
                label: Text(
                  isLoading
                      ? 'Đang xử lý...'
                      : imageData.isEmpty
                      ? 'Chọn ảnh'
                      : 'Thay ảnh',
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
