import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('CRUD Starter')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 560),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    padding: const EdgeInsets.all(28),
                    decoration: BoxDecoration(
                      color: colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(28),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          Icons.storage_rounded,
                          size: 64,
                          color: colorScheme.onPrimaryContainer,
                        ),
                        const SizedBox(height: 20),
                        Text(
                          'Project đã sẵn sàng',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall
                              ?.copyWith(fontWeight: FontWeight.w700),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'Chờ cấu trúc dữ liệu và yêu cầu chính thức để triển khai ứng dụng.',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  const _ReadyItem(
                    icon: Icons.phone_android_rounded,
                    title: 'Flutter Android',
                    subtitle: 'Cấu hình build và Material 3',
                  ),
                  const _ReadyItem(
                    icon: Icons.storage_rounded,
                    title: 'SQLite',
                    subtitle: 'sqflite, path và foreign keys',
                  ),
                  const _ReadyItem(
                    icon: Icons.account_tree_rounded,
                    title: 'Cấu trúc sạch',
                    subtitle: 'Tách app, core và feature',
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ReadyItem extends StatelessWidget {
  const _ReadyItem({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
        leading: CircleAvatar(child: Icon(icon)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(subtitle),
        trailing: Icon(
          Icons.check_circle_rounded,
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
    );
  }
}
