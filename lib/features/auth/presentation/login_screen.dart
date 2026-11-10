import 'package:flutter/material.dart';

import '../../../app/app_bootstrap.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/validators.dart';
import '../../../core/widgets/record_mark.dart';
import '../data/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({required this.authService, super.key});

  final AuthService authService;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    if (AppBootstrap.useFirebaseEmulator) {
      _emailController.text = AppBootstrap.demoAdminEmail;
      _passwordController.text = AppBootstrap.demoAdminPassword;
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await widget.authService.signIn(
        email: _emailController.text,
        password: _passwordController.text,
      );
    } on AuthFailure catch (error) {
      if (mounted) {
        setState(() => _errorMessage = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth >= 860;
            return Row(
              children: [
                Expanded(
                  flex: isWide ? 11 : 1,
                  child: _LoginForm(
                    formKey: _formKey,
                    emailController: _emailController,
                    passwordController: _passwordController,
                    obscurePassword: _obscurePassword,
                    isLoading: _isLoading,
                    errorMessage: _errorMessage,
                    onTogglePassword: () =>
                        setState(() => _obscurePassword = !_obscurePassword),
                    onSubmit: _submit,
                  ),
                ),
                if (isWide) const Expanded(flex: 9, child: _RegistryPanel()),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _LoginForm extends StatelessWidget {
  const _LoginForm({
    required this.formKey,
    required this.emailController,
    required this.passwordController,
    required this.obscurePassword,
    required this.isLoading,
    required this.errorMessage,
    required this.onTogglePassword,
    required this.onSubmit,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final bool obscurePassword;
  final bool isLoading;
  final String? errorMessage;
  final VoidCallback onTogglePassword;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(28),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 440),
          child: Form(
            key: formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Align(
                  alignment: Alignment.centerLeft,
                  child: RecordMark(),
                ),
                const SizedBox(height: 64),
                Text(
                  'Truy cập hồ sơ\nngười dùng.',
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    fontWeight: FontWeight.w900,
                    height: 1.05,
                    letterSpacing: -1.8,
                  ),
                ),
                const SizedBox(height: 14),
                const Text(
                  'Đăng nhập bằng tài khoản quản trị để tiếp tục.',
                  style: TextStyle(color: AppColors.inkMuted, fontSize: 16),
                ),
                const SizedBox(height: 36),
                TextFormField(
                  controller: emailController,
                  validator: Validators.email,
                  keyboardType: TextInputType.emailAddress,
                  autofillHints: const [AutofillHints.username],
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(
                    labelText: 'Email quản trị',
                    prefixIcon: Icon(Icons.alternate_email_rounded),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: passwordController,
                  validator: Validators.password,
                  obscureText: obscurePassword,
                  autofillHints: const [AutofillHints.password],
                  onFieldSubmitted: (_) => onSubmit(),
                  decoration: InputDecoration(
                    labelText: 'Mật khẩu',
                    prefixIcon: const Icon(Icons.lock_outline_rounded),
                    suffixIcon: IconButton(
                      onPressed: onTogglePassword,
                      tooltip: obscurePassword
                          ? 'Hiện mật khẩu'
                          : 'Ẩn mật khẩu',
                      icon: Icon(
                        obscurePassword
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                      ),
                    ),
                  ),
                ),
                if (errorMessage != null) ...[
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.coral.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      errorMessage!,
                      style: const TextStyle(
                        color: Color(0xFFB42318),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: 22),
                FilledButton.icon(
                  onPressed: isLoading ? null : onSubmit,
                  icon: isLoading
                      ? const SizedBox.square(
                          dimension: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.arrow_forward_rounded),
                  label: Text(
                    isLoading ? 'Đang xác thực...' : 'Vào trang quản trị',
                  ),
                ),
                if (AppBootstrap.useFirebaseEmulator) ...[
                  const SizedBox(height: 22),
                  const Text(
                    'CHẾ ĐỘ DEMO · Thông tin đăng nhập đã được điền sẵn',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: AppColors.inkMuted,
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RegistryPanel extends StatelessWidget {
  const _RegistryPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(18),
      padding: const EdgeInsets.all(48),
      decoration: BoxDecoration(
        color: AppColors.ink,
        borderRadius: BorderRadius.circular(28),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              _StatusDot(),
              SizedBox(width: 10),
              Text(
                'SYSTEM ONLINE',
                style: TextStyle(
                  color: AppColors.mint,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1.5,
                ),
              ),
            ],
          ),
          const Spacer(),
          Text(
            '01',
            style: Theme.of(context).textTheme.displayLarge?.copyWith(
              color: AppColors.mint,
              fontWeight: FontWeight.w200,
              fontSize: 94,
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'Một nơi duy nhất để quản lý hồ sơ, ảnh đại diện và quyền truy cập.',
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.w800,
              height: 1.2,
            ),
          ),
          const SizedBox(height: 36),
          Container(height: 1, color: Colors.white24),
          const SizedBox(height: 24),
          const Wrap(
            spacing: 20,
            runSpacing: 12,
            children: [
              _PanelTag(label: 'FIREBASE'),
              _PanelTag(label: 'WEB + MOBILE'),
              _PanelTag(label: 'ADMIN'),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatusDot extends StatelessWidget {
  const _StatusDot();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 9,
      height: 9,
      decoration: const BoxDecoration(
        color: AppColors.mint,
        shape: BoxShape.circle,
      ),
    );
  }
}

class _PanelTag extends StatelessWidget {
  const _PanelTag({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: const TextStyle(
        color: Colors.white54,
        fontSize: 10,
        fontWeight: FontWeight.w800,
        letterSpacing: 1.2,
      ),
    );
  }
}
