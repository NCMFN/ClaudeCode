---
name: laravel-verification
description: Verification loop for Laravel projects: env checks, linting, static analysis, tests with coverage, security scans, and deployment readiness.
origin: ECC
---

# Laravel 验证流程

在发起 PR 前、进行重大更改后以及部署前运行。

## 何时使用

* 为 Laravel 项目开启拉取请求之前
* 在重大重构或依赖项升级之后
* 用于暂存或生产环境的预部署验证
* 运行完整的 lint -> 测试 -> 安全 -> 部署就绪流水线

## 工作原理

* 按顺序运行各个阶段，从环境检查到部署就绪，每一层都建立在上一层的基础上。
* 环境和 Composer 检查是所有其他步骤的关卡；如果它们失败，立即停止。
* Linting/静态分析应在运行完整测试和覆盖率检查之前保持干净。
* 安全和迁移审查在测试之后进行，以便在数据或发布步骤之前验证行为。
* 构建/部署就绪以及队列/调度程序检查是最后的关卡；任何失败都会阻止发布。

## 阶段 1：环境检查

```bash
php -v
composer --version
php artisan --version
```

* 验证 `.env` 存在且所需的键存在
* 确认生产环境的 `APP_DEBUG=false`
* 确认 `APP_ENV` 与目标部署环境匹配（`production`、`staging`）

如果在本地使用 Laravel Sail：

```bash
./vendor/bin/sail php -v
./vendor/bin/sail artisan --version
```

## 阶段 1.5：Composer 和自动加载

```bash
composer validate
composer dump-autoload -o
```

## 阶段 2：Linting 和静态分析

```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
```

如果你的项目使用 Psalm 而不是 PHPStan：

```bash
vendor/bin/psalm
```

## 阶段 3：测试和覆盖率

```bash
php artisan test
```

覆盖率（CI）：

```bash
XDEBUG_MODE=coverage php artisan test --coverage
```

CI 示例（格式化 -> 静态分析 -> 测试）：

```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
XDEBUG_MODE=coverage php artisan test --coverage
```

## 阶段 4：安全和依赖项检查

```bash
composer audit
```

## 阶段 5：数据库和迁移

```bash
php artisan migrate --pretend
php artisan migrate:status
```

* 仔细审查破坏性迁移
* 确保迁移文件名遵循 `Y_m_d_His_*`（例如 `2025_03_14_154210_create_orders_table.php`）并清晰地描述变更
* 确保可以回滚
* 验证 `down()` 方法，并避免在没有明确备份的情况下造成不可逆的数据丢失

## 阶段 6：构建和部署就绪

```bash
php artisan optimize:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

* 确保缓存预热在生产配置中成功
* 验证队列工作器和调度程序已配置
* 确认 `storage/` 和 `bootstrap/cache/` 在目标环境中可写

## 阶段 7：队列和调度程序检查

```bash
php artisan schedule:list
php artisan queue:failed
```

如果使用了 Horizon：

```bash
php artisan horizon:status
```

如果 `queue:monitor` 可用，使用它来检查积压而不处理作业：

```bash
php artisan queue:monitor default --max=100
```

主动验证（仅限暂存环境）：向专用队列分发一个无操作作业，并运行单个工作器来处理它（确保配置了非 `sync` 队列连接）。

```bash
php artisan tinker --execute="dispatch((new App\\Jobs\\QueueHealthcheck())->onQueue('healthcheck'))"
php artisan queue:work --once --queue=healthcheck
```

验证作业产生了预期的副作用（日志条目、健康检查表行或指标）。

仅在处理测试作业安全的非生产环境中运行此步骤。

## 示例

最小流程：

```bash
php -v
composer --version
php artisan --version
composer validate
vendor/bin/pint --test
vendor/bin/phpstan analyse
php artisan test
composer audit
php artisan migrate --pretend
php artisan config:cache
php artisan queue:failed
```

CI 风格流水线：

```bash
composer validate
composer dump-autoload -o
vendor/bin/pint --test
vendor/bin/phpstan analyse
XDEBUG_MODE=coverage php artisan test --coverage
composer audit
php artisan migrate --pretend
php artisan optimize:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan schedule:list
```
