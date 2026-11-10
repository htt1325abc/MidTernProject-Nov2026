import 'package:flutter/material.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/record_mark.dart';
import '../../auth/data/auth_service.dart';
import '../data/user_repository.dart';
import '../domain/user_record.dart';
import 'user_avatar.dart';
import 'user_form_dialog.dart';

enum UserSort { nameAscending, nameDescending, emailAscending }

String _maskPassword(String password) {
  final length = password.length.clamp(6, 12);
  return List.filled(length, '•').join();
}

class UserDashboard extends StatefulWidget {
  const UserDashboard({
    required this.authService,
    required this.repository,
    super.key,
  });

  final AuthService authService;
  final UserRepository repository;

  @override
  State<UserDashboard> createState() => _UserDashboardState();
}

class _UserDashboardState extends State<UserDashboard> {
  final _searchController = TextEditingController();
  String _query = '';
  UserSort _sort = UserSort.nameAscending;
  bool _showPasswords = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  List<UserRecord> _filterAndSort(List<UserRecord> users) {
    final query = _query.trim().toLowerCase();
    final filtered = users.where((user) {
      return query.isEmpty ||
          user.hoten.toLowerCase().contains(query) ||
          user.email.toLowerCase().contains(query);
    }).toList();

    switch (_sort) {
      case UserSort.nameAscending:
        filtered.sort(
          (a, b) => a.hoten.toLowerCase().compareTo(b.hoten.toLowerCase()),
        );
        break;
      case UserSort.nameDescending:
        filtered.sort(
          (a, b) => b.hoten.toLowerCase().compareTo(a.hoten.toLowerCase()),
        );
        break;
      case UserSort.emailAscending:
        filtered.sort(
          (a, b) => a.email.toLowerCase().compareTo(b.email.toLowerCase()),
        );
        break;
    }
    return filtered;
  }

  Future<void> _openForm([UserRecord? existing]) async {
    final saved = await showUserFormDialog(
      context,
      repository: widget.repository,
      existing: existing,
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            existing == null
                ? 'Đã thêm người dùng.'
                : 'Đã cập nhật người dùng.',
          ),
        ),
      );
    }
  }

  Future<void> _delete(UserRecord user) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Xóa người dùng?'),
        content: Text(
          'Hồ sơ của ${user.hoten} sẽ bị xóa khỏi Firebase. Thao tác này không thể hoàn tác.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Giữ lại'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppColors.coral),
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('Xóa hồ sơ'),
          ),
        ],
      ),
    );

    if (confirmed != true) {
      return;
    }

    try {
      await widget.repository.delete(user.key);
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Đã xóa người dùng.')));
      }
    } on UserRepositoryFailure catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(error.message)));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 940;
        return Scaffold(
          body: SafeArea(
            child: Row(
              children: [
                if (isWide)
                  _SideRail(
                    onAdd: _openForm,
                    onSignOut: widget.authService.signOut,
                  ),
                Expanded(
                  child: StreamBuilder<List<UserRecord>>(
                    stream: widget.repository.watchUsers(),
                    builder: (context, snapshot) {
                      return _DashboardContent(
                        users: _filterAndSort(snapshot.data ?? const []),
                        totalUsers: snapshot.data?.length ?? 0,
                        isLoading:
                            snapshot.connectionState == ConnectionState.waiting,
                        error: snapshot.error,
                        isWide: isWide,
                        searchController: _searchController,
                        sort: _sort,
                        showPasswords: _showPasswords,
                        onSearch: (value) => setState(() => _query = value),
                        onSort: (value) => setState(() => _sort = value),
                        onTogglePasswords: () =>
                            setState(() => _showPasswords = !_showPasswords),
                        onAdd: _openForm,
                        onEdit: _openForm,
                        onDelete: _delete,
                        onSignOut: widget.authService.signOut,
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
          floatingActionButton: isWide
              ? null
              : FloatingActionButton.extended(
                  onPressed: _openForm,
                  icon: const Icon(Icons.person_add_alt_1_rounded),
                  label: const Text('Thêm người dùng'),
                ),
        );
      },
    );
  }
}

class _SideRail extends StatelessWidget {
  const _SideRail({required this.onAdd, required this.onSignOut});

  final VoidCallback onAdd;
  final Future<void> Function() onSignOut;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 252,
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: AppColors.ink,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const _InverseRecordMark(),
          const SizedBox(height: 48),
          const _RailItem(
            icon: Icons.people_alt_rounded,
            label: 'Người dùng',
            selected: true,
          ),
          const SizedBox(height: 10),
          FilledButton.icon(
            onPressed: onAdd,
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.mint,
              foregroundColor: AppColors.ink,
            ),
            icon: const Icon(Icons.add_rounded),
            label: const Text('Tạo hồ sơ'),
          ),
          const Spacer(),
          const _DatabaseStatus(),
          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: onSignOut,
            style: TextButton.styleFrom(foregroundColor: Colors.white70),
            icon: const Icon(Icons.logout_rounded),
            label: const Text('Đăng xuất'),
          ),
        ],
      ),
    );
  }
}

class _InverseRecordMark extends StatelessWidget {
  const _InverseRecordMark();

  @override
  Widget build(BuildContext context) {
    return const Row(
      children: [
        Text(
          'U/',
          style: TextStyle(
            color: AppColors.mint,
            fontWeight: FontWeight.w900,
            fontSize: 24,
          ),
        ),
        SizedBox(width: 8),
        Expanded(
          child: Text(
            'USER\nREGISTRY',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w900,
              fontSize: 12,
              height: 1.05,
              letterSpacing: 1.1,
            ),
          ),
        ),
      ],
    );
  }
}

class _RailItem extends StatelessWidget {
  const _RailItem({
    required this.icon,
    required this.label,
    required this.selected,
  });

  final IconData icon;
  final String label;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
      decoration: BoxDecoration(
        color: selected ? Colors.white12 : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: selected ? AppColors.mint : Colors.white54),
          const SizedBox(width: 12),
          Text(
            label,
            style: TextStyle(
              color: selected ? Colors.white : Colors.white54,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class _DatabaseStatus extends StatelessWidget {
  const _DatabaseStatus();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.white12),
        borderRadius: BorderRadius.circular(14),
      ),
      child: const Row(
        children: [
          Icon(Icons.cloud_done_outlined, color: AppColors.mint, size: 20),
          SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'FIREBASE',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w800,
                    fontSize: 11,
                  ),
                ),
                Text(
                  'Đang đồng bộ',
                  style: TextStyle(color: Colors.white54, fontSize: 11),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DashboardContent extends StatelessWidget {
  const _DashboardContent({
    required this.users,
    required this.totalUsers,
    required this.isLoading,
    required this.error,
    required this.isWide,
    required this.searchController,
    required this.sort,
    required this.showPasswords,
    required this.onSearch,
    required this.onSort,
    required this.onTogglePasswords,
    required this.onAdd,
    required this.onEdit,
    required this.onDelete,
    required this.onSignOut,
  });

  final List<UserRecord> users;
  final int totalUsers;
  final bool isLoading;
  final Object? error;
  final bool isWide;
  final TextEditingController searchController;
  final UserSort sort;
  final bool showPasswords;
  final ValueChanged<String> onSearch;
  final ValueChanged<UserSort> onSort;
  final VoidCallback onTogglePasswords;
  final VoidCallback onAdd;
  final ValueChanged<UserRecord> onEdit;
  final ValueChanged<UserRecord> onDelete;
  final Future<void> Function() onSignOut;

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.fromLTRB(
              isWide ? 30 : 18,
              isWide ? 28 : 18,
              isWide ? 30 : 18,
              0,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (!isWide)
                  Row(
                    children: [
                      const RecordMark(compact: true),
                      const Spacer(),
                      IconButton(
                        onPressed: onSignOut,
                        tooltip: 'Đăng xuất',
                        icon: const Icon(Icons.logout_rounded),
                      ),
                    ],
                  ),
                SizedBox(height: isWide ? 0 : 28),
                _Header(totalUsers: totalUsers),
                const SizedBox(height: 24),
                _Toolbar(
                  searchController: searchController,
                  sort: sort,
                  showPasswords: showPasswords,
                  isWide: isWide,
                  onSearch: onSearch,
                  onSort: onSort,
                  onTogglePasswords: onTogglePasswords,
                  onAdd: onAdd,
                ),
                const SizedBox(height: 18),
              ],
            ),
          ),
        ),
        if (isLoading)
          const SliverFillRemaining(
            hasScrollBody: false,
            child: Center(child: CircularProgressIndicator()),
          )
        else if (error != null)
          SliverFillRemaining(
            hasScrollBody: false,
            child: _ErrorState(error: error!),
          )
        else if (users.isEmpty)
          SliverFillRemaining(
            hasScrollBody: false,
            child: _EmptyState(onAdd: onAdd),
          )
        else if (isWide)
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(30, 0, 30, 30),
            sliver: SliverToBoxAdapter(
              child: _UserTable(
                users: users,
                showPasswords: showPasswords,
                onEdit: onEdit,
                onDelete: onDelete,
              ),
            ),
          )
        else
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(18, 0, 18, 100),
            sliver: SliverList.separated(
              itemCount: users.length,
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemBuilder: (context, index) => _UserCard(
                index: index,
                user: users[index],
                showPassword: showPasswords,
                onEdit: () => onEdit(users[index]),
                onDelete: () => onDelete(users[index]),
              ),
            ),
          ),
      ],
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.totalUsers});

  final int totalUsers;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'ADMIN / DIRECTORY',
                style: TextStyle(
                  color: AppColors.electric,
                  fontWeight: FontWeight.w900,
                  fontSize: 11,
                  letterSpacing: 1.5,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Hồ sơ người dùng',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w900,
                  letterSpacing: -1.2,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Thêm, kiểm tra và cập nhật dữ liệu từ một nơi.',
                style: TextStyle(color: AppColors.inkMuted),
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: AppColors.paper,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.line),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '$totalUsers',
                style: const TextStyle(
                  color: AppColors.ink,
                  fontSize: 25,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const Text(
                'HỒ SƠ',
                style: TextStyle(
                  color: AppColors.inkMuted,
                  fontSize: 9,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1.1,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _Toolbar extends StatelessWidget {
  const _Toolbar({
    required this.searchController,
    required this.sort,
    required this.showPasswords,
    required this.isWide,
    required this.onSearch,
    required this.onSort,
    required this.onTogglePasswords,
    required this.onAdd,
  });

  final TextEditingController searchController;
  final UserSort sort;
  final bool showPasswords;
  final bool isWide;
  final ValueChanged<String> onSearch;
  final ValueChanged<UserSort> onSort;
  final VoidCallback onTogglePasswords;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    final search = TextField(
      controller: searchController,
      onChanged: onSearch,
      decoration: const InputDecoration(
        hintText: 'Tìm theo họ tên hoặc email...',
        prefixIcon: Icon(Icons.search_rounded),
      ),
    );
    final controls = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        PopupMenuButton<UserSort>(
          initialValue: sort,
          tooltip: 'Sắp xếp',
          onSelected: onSort,
          itemBuilder: (_) => const [
            PopupMenuItem(
              value: UserSort.nameAscending,
              child: Text('Tên A–Z'),
            ),
            PopupMenuItem(
              value: UserSort.nameDescending,
              child: Text('Tên Z–A'),
            ),
            PopupMenuItem(
              value: UserSort.emailAscending,
              child: Text('Email A–Z'),
            ),
          ],
          icon: const Icon(Icons.sort_by_alpha_rounded),
        ),
        IconButton(
          onPressed: onTogglePasswords,
          tooltip: showPasswords ? 'Ẩn mật khẩu' : 'Hiện mật khẩu',
          icon: Icon(
            showPasswords
                ? Icons.visibility_off_outlined
                : Icons.visibility_outlined,
          ),
        ),
        if (isWide) ...[
          const SizedBox(width: 10),
          FilledButton.icon(
            onPressed: onAdd,
            icon: const Icon(Icons.person_add_alt_1_rounded),
            label: const Text('Thêm người dùng'),
          ),
        ],
      ],
    );

    if (isWide) {
      return Row(
        children: [
          Expanded(child: search),
          const SizedBox(width: 12),
          controls,
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        search,
        const SizedBox(height: 8),
        Align(alignment: Alignment.centerRight, child: controls),
      ],
    );
  }
}

class _UserTable extends StatelessWidget {
  const _UserTable({
    required this.users,
    required this.showPasswords,
    required this.onEdit,
    required this.onDelete,
  });

  final List<UserRecord> users;
  final bool showPasswords;
  final ValueChanged<UserRecord> onEdit;
  final ValueChanged<UserRecord> onDelete;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.paper,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.line),
      ),
      clipBehavior: Clip.antiAlias,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(AppColors.ink),
          headingTextStyle: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w800,
            fontSize: 11,
            letterSpacing: 0.7,
          ),
          dataRowMinHeight: 76,
          dataRowMaxHeight: 76,
          dividerThickness: 1,
          columns: const [
            DataColumn(label: Text('HỒ SƠ')),
            DataColumn(label: Text('EMAIL')),
            DataColumn(label: Text('MẬT KHẨU')),
            DataColumn(label: Text('THAO TÁC')),
          ],
          rows: [
            for (final user in users)
              DataRow(
                cells: [
                  DataCell(
                    SizedBox(
                      width: 260,
                      child: Row(
                        children: [
                          UserAvatar(imageData: user.hinhanh, size: 48),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              user.hoten,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  DataCell(
                    SizedBox(width: 250, child: SelectableText(user.email)),
                  ),
                  DataCell(
                    SizedBox(
                      width: 150,
                      child: Text(
                        showPasswords
                            ? user.matkhau
                            : _maskPassword(user.matkhau),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
                  DataCell(
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          onPressed: () => onEdit(user),
                          tooltip: 'Sửa ${user.hoten}',
                          icon: const Icon(Icons.edit_outlined),
                        ),
                        IconButton(
                          onPressed: () => onDelete(user),
                          tooltip: 'Xóa ${user.hoten}',
                          color: AppColors.coral,
                          icon: const Icon(Icons.delete_outline_rounded),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _UserCard extends StatelessWidget {
  const _UserCard({
    required this.index,
    required this.user,
    required this.showPassword,
    required this.onEdit,
    required this.onDelete,
  });

  final int index;
  final UserRecord user;
  final bool showPassword;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                UserAvatar(imageData: user.hinhanh, size: 64),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'RECORD ${(index + 1).toString().padLeft(2, '0')}',
                        style: const TextStyle(
                          color: AppColors.electric,
                          fontSize: 9,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1.1,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        user.hoten,
                        style: const TextStyle(
                          fontWeight: FontWeight.w900,
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        user.email,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: AppColors.inkMuted),
                      ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (value) =>
                      value == 'edit' ? onEdit() : onDelete(),
                  itemBuilder: (_) => const [
                    PopupMenuItem(value: 'edit', child: Text('Sửa hồ sơ')),
                    PopupMenuItem(value: 'delete', child: Text('Xóa hồ sơ')),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.canvas,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.key_rounded,
                    size: 18,
                    color: AppColors.inkMuted,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      showPassword ? user.matkhau : _maskPassword(user.matkhau),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.onAdd});

  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.person_search_rounded,
              size: 58,
              color: AppColors.inkMuted,
            ),
            const SizedBox(height: 18),
            const Text(
              'Chưa có hồ sơ phù hợp',
              style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 8),
            const Text(
              'Thêm người dùng đầu tiên hoặc thay đổi từ khóa tìm kiếm.',
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.inkMuted),
            ),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: onAdd,
              icon: const Icon(Icons.add_rounded),
              label: const Text('Tạo hồ sơ'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.error});

  final Object error;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.cloud_off_rounded,
              size: 58,
              color: AppColors.coral,
            ),
            const SizedBox(height: 16),
            const Text(
              'Không tải được dữ liệu',
              style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 8),
            Text(
              '$error',
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppColors.inkMuted),
            ),
          ],
        ),
      ),
    );
  }
}
