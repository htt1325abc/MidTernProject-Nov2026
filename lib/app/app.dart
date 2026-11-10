import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

import '../core/theme/app_theme.dart';
import '../features/auth/data/auth_service.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/users/data/user_repository.dart';
import '../features/users/presentation/user_dashboard.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'User Registry',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: AuthGate(
        authService: AuthService(),
        userRepository: UserRepository(),
      ),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({
    required this.authService,
    required this.userRepository,
    super.key,
  });

  final AuthService authService;
  final UserRepository userRepository;

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: authService.authStateChanges,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        if (snapshot.data == null) {
          return LoginScreen(authService: authService);
        }

        return UserDashboard(
          authService: authService,
          repository: userRepository,
        );
      },
    );
  }
}
