# AI垂域营销系统数据库设计

## 数据库表结构设计

### 1. 用户管理模块

#### 1.1 用户表 (users)

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    phone VARCHAR(20) COMMENT '手机号',
    role ENUM('admin', 'manager', 'sales', 'operator') DEFAULT 'sales' COMMENT '角色：管理员、员工',
    permissions JSON COMMENT '用户权限配置',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    is_del TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_time TIMESTAMP NULL COMMENT '最后登录时间',
    FOREIGN KEY (dept_id) REFERENCES departments(id) ON DELETE RESTRICT,
    INDEX idx_dept_id (dept_id),
    INDEX idx_role (role),
    INDEX idx_is_del (is_del)
);
```

#### 1.2 客户表 (customers)

```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL COMMENT '客户名称/昵称',
    platform_type ENUM('xiaohongshu', 'douyin', 'wechat_video', 'wechat', 'other') NOT NULL COMMENT '来源平台',
    platform_user_id VARCHAR(100) COMMENT '平台用户ID',
    platform_username VARCHAR(100) COMMENT '平台用户名',
    avatar_url VARCHAR(500) COMMENT '头像链接',
    phone VARCHAR(20) COMMENT '联系电话',
    wechat VARCHAR(100) COMMENT '微信号',
    email VARCHAR(100) COMMENT '邮箱',
    gender TINYINT COMMENT '性别：0-未知，1-男，2-女',
    age_range VARCHAR(20) COMMENT '年龄段',
    location VARCHAR(100) COMMENT '地理位置',
    interests JSON COMMENT '兴趣标签数组',
    source_type ENUM('fan', 'comment', 'private_msg', 'wechat_add', 'manual') NOT NULL COMMENT '获取方式：粉丝、评论、私信、微信添加、手动添加',
    source_account_id BIGINT COMMENT '来源账户ID',
    source_content TEXT COMMENT '来源内容/备注',
    customer_level TINYINT DEFAULT 1 COMMENT '客户等级：1-潜在客户，2-意向客户，3-成交客户',
    sales_user_id BIGINT NOT NULL COMMENT '负责销售',
    status TINYINT DEFAULT 1 COMMENT '状态：0-无效，1-有效，2-已流失',
    is_del TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sales_user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (source_account_id) REFERENCES platform_accounts(id) ON DELETE SET NULL,
    INDEX idx_platform_type (platform_type),
    INDEX idx_sales_user_id (sales_user_id),
    INDEX idx_source_type (source_type),
    INDEX idx_customer_level (customer_level),
    INDEX idx_is_del (is_del)
);
```

#### 1.3 客户跟进记录表 (customer_follow_logs)

```sql
CREATE TABLE customer_follow_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    sales_user_id BIGINT NOT NULL,
    follow_type ENUM('call', 'wechat', 'meeting', 'email', 'other') NOT NULL COMMENT '跟进方式',
    follow_content TEXT NOT NULL COMMENT '跟进内容',
    follow_result ENUM('no_response', 'interested', 'not_interested', 'deal', 'follow_up') COMMENT '跟进结果',
    next_follow_time TIMESTAMP NULL COMMENT '下次跟进时间',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (sales_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_customer_id (customer_id),
    INDEX idx_sales_user_id (sales_user_id),
    INDEX idx_next_follow_time (next_follow_time)
);
```

### 2. 平台数据模块

#### 2.1 平台账户表 (platform_accounts)

```sql
CREATE TABLE platform_accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    platform_type ENUM('xiaohongshu', 'douyin', 'wechat_video') NOT NULL COMMENT '平台类型',
    account_url VARCHAR(500) NOT NULL COMMENT '账户主页链接',
    account_name VARCHAR(100) COMMENT '账户名称',
    account_id VARCHAR(100) COMMENT '平台账户ID',
    profile_info JSON COMMENT '个人简介信息',
    follower_count INT DEFAULT 0 COMMENT '粉丝数',
    following_count INT DEFAULT 0 COMMENT '关注数',
    post_count INT DEFAULT 0 COMMENT '发布内容数',
    parse_status TINYINT DEFAULT 0 COMMENT '解析状态：0-待解析，1-解析中，2-已解析，3-解析失败',
    last_parsed_time TIMESTAMP NULL COMMENT '最后解析时间',
    user_id BIGINT NOT NULL COMMENT '关联用户',
    is_del TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_platform_type (platform_type),
    INDEX idx_user_id (user_id),
    INDEX idx_is_del (is_del)
);
```

#### 2.2 小红书数据表 (xiaohongshu_posts)

```sql
CREATE TABLE xiaohongshu_posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    post_url VARCHAR(500) NOT NULL COMMENT '笔记链接',
    post_id VARCHAR(100) COMMENT '平台内容ID',
    title VARCHAR(200) COMMENT '标题',
    content TEXT COMMENT '内容',
    images JSON COMMENT '图片链接数组',
    tags JSON COMMENT '标签数组',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    share_count INT DEFAULT 0 COMMENT '分享数',
    collect_count INT DEFAULT 0 COMMENT '收藏数',
    published_time TIMESTAMP COMMENT '发布时间',
    ai_summary TEXT COMMENT '大模型总结内容',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES platform_accounts(id) ON DELETE CASCADE,
    INDEX idx_account_id (account_id),
    INDEX idx_published_time (published_time)
);
```

#### 2.3 抖音数据表 (douyin_posts)

```sql
CREATE TABLE douyin_posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    post_url VARCHAR(500) NOT NULL COMMENT '视频链接',
    post_id VARCHAR(100) COMMENT '平台内容ID',
    title VARCHAR(200) COMMENT '标题',
    content TEXT COMMENT '内容描述',
    video_url VARCHAR(500) COMMENT '视频地址',
    cover_url VARCHAR(500) COMMENT '封面图片',
    duration INT COMMENT '视频时长（秒）',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    share_count INT DEFAULT 0 COMMENT '转发数',
    play_count INT DEFAULT 0 COMMENT '播放数',
    published_time TIMESTAMP COMMENT '发布时间',
    ai_summary TEXT COMMENT '大模型总结内容',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES platform_accounts(id) ON DELETE CASCADE,
    INDEX idx_account_id (account_id),
    INDEX idx_published_time (published_time)
);
```

#### 2.4 微信视频号数据表 (wechat_video_posts)

```sql
CREATE TABLE wechat_video_posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    post_url VARCHAR(500) NOT NULL COMMENT '视频链接',
    post_id VARCHAR(100) COMMENT '平台内容ID',
    title VARCHAR(200) COMMENT '标题',
    content TEXT COMMENT '内容描述',
    video_url VARCHAR(500) COMMENT '视频地址',
    cover_url VARCHAR(500) COMMENT '封面图片',
    duration INT COMMENT '视频时长（秒）',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    share_count INT DEFAULT 0 COMMENT '转发数',
    view_count INT DEFAULT 0 COMMENT '观看数',
    published_time TIMESTAMP COMMENT '发布时间',
    ai_summary TEXT COMMENT '大模型总结内容',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES platform_accounts(id) ON DELETE CASCADE,
    INDEX idx_account_id (account_id),
    INDEX idx_published_time (published_time)
);
```

### 3. 大模型分析模块

#### 3.1 大模型分析任务表 (ai_analysis_tasks)

```sql
CREATE TABLE ai_analysis_tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_type ENUM('content_analysis', 'user_analysis', 'trend_analysis') NOT NULL COMMENT '分析类型',
    target_type ENUM('post', 'video', 'account', 'keyword') NOT NULL COMMENT '分析目标类型',
    target_id BIGINT COMMENT '目标ID',
    analysis_prompt TEXT COMMENT '分析提示词',
    analysis_result JSON COMMENT '分析结果',
    status TINYINT DEFAULT 0 COMMENT '状态：0-待处理，1-处理中，2-已完成，3-失败',
    error_message TEXT COMMENT '错误信息',
    user_id BIGINT NOT NULL COMMENT '创建用户',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_task_type (task_type),
    INDEX idx_status (status),
    INDEX idx_user_id (user_id)
);
```

#### 3.2 知识库表 (knowledge_bases)

```sql
CREATE TABLE knowledge_bases (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    kb_name VARCHAR(100) NOT NULL COMMENT '知识库名称',
    kb_description TEXT COMMENT '知识库描述',
    kb_content LONGTEXT COMMENT '知识库内容',
    kb_type TINYINT DEFAULT 1 COMMENT '知识库类型：1-通用，2-行业专用，3-客户专用',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    user_id BIGINT NOT NULL COMMENT '创建用户',
    is_del TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_del (is_del)
);
```

### 4. 机器人配置模块

#### 4.1 机器人配置表 (bot_configs)

```sql
CREATE TABLE bot_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bot_name VARCHAR(100) NOT NULL COMMENT '机器人名称',
    bot_type ENUM('public', 'private') NOT NULL COMMENT '机器人类型：公域、私域',
    knowledge_base_ids JSON COMMENT '关联的知识库ID数组',
    platform_account_ids JSON COMMENT '关联的平台账户ID数组',
    wechat_config JSON COMMENT '微信/企业微信配置',
    auto_reply_rules JSON COMMENT '自动回复规则',
    reply_delay_min INT DEFAULT 5 COMMENT '回复延迟最小值（秒）',
    reply_delay_max INT DEFAULT 30 COMMENT '回复延迟最大值（秒）',
    daily_reply_limit INT DEFAULT 100 COMMENT '每日回复限制',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    user_id BIGINT NOT NULL COMMENT '所属用户',
    is_del TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_del (is_del)
);
```

#### 4.2 关键词过滤表 (keyword_filters)

```sql
CREATE TABLE keyword_filters (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bot_config_id BIGINT NOT NULL COMMENT '关联机器人配置',
    filter_type ENUM('blacklist', 'whitelist', 'sensitive') NOT NULL COMMENT '过滤类型：黑名单、白名单、敏感词',
    keyword VARCHAR(200) NOT NULL COMMENT '关键词',
    match_type ENUM('exact', 'contains', 'regex') DEFAULT 'contains' COMMENT '匹配方式：精确匹配、包含匹配、正则匹配',
    action ENUM('block', 'allow', 'alert', 'auto_reply') NOT NULL COMMENT '触发动作：阻止、允许、警告、自动回复',
    auto_reply_content TEXT COMMENT '自动回复内容',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bot_config_id) REFERENCES bot_configs(id) ON DELETE CASCADE,
    INDEX idx_bot_config_id (bot_config_id),
    INDEX idx_filter_type (filter_type),
    INDEX idx_keyword (keyword)
);
```

```

#### 4.3 公域机器人数据表 (public_bot_logs)
```sql
CREATE TABLE public_bot_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bot_config_id BIGINT NOT NULL,
    platform_type ENUM('xiaohongshu', 'douyin', 'wechat_video') NOT NULL,
    target_account_id BIGINT COMMENT '目标账户ID',
    target_content_id BIGINT COMMENT '目标内容ID',
    interaction_type ENUM('comment', 'like', 'follow', 'private_msg') NOT NULL COMMENT '互动类型',
    message_content TEXT COMMENT '消息内容',
    response_content TEXT COMMENT '回复内容',
    status ENUM('pending', 'sent', 'failed') DEFAULT 'pending' COMMENT '状态',
    error_message TEXT COMMENT '错误信息',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bot_config_id) REFERENCES bot_configs(id) ON DELETE CASCADE,
    INDEX idx_bot_config_id (bot_config_id),
    INDEX idx_platform_type (platform_type),
    INDEX idx_interaction_type (interaction_type)
);
```

#### 4.4 私域机器人数据表 (private_bot_logs)

```sql
CREATE TABLE private_bot_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bot_config_id BIGINT NOT NULL,
    bot_type ENUM('wechat', 'enterprise_wechat') NOT NULL,
    user_openid VARCHAR(100) NOT NULL COMMENT '用户OpenID',
    user_nickname VARCHAR(100) COMMENT '用户昵称',
    message_type ENUM('text', 'image', 'voice', 'video', 'file') NOT NULL COMMENT '消息类型',
    user_message TEXT COMMENT '用户消息内容',
    bot_reply TEXT COMMENT '机器人回复内容',
    is_auto_reply TINYINT DEFAULT 1 COMMENT '是否自动回复',
    conversation_id VARCHAR(100) COMMENT '会话ID',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bot_config_id) REFERENCES bot_configs(id) ON DELETE CASCADE,
    INDEX idx_bot_config_id (bot_config_id),
    INDEX idx_user_openid (user_openid),
    INDEX idx_conversation_id (conversation_id)
);
```

### 5. 定时任务模块

#### 5.1 定时任务表 (scheduled_tasks)

```sql
CREATE TABLE scheduled_tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
    task_description TEXT COMMENT '任务描述',
    task_content TEXT NOT NULL COMMENT '投放内容',
    target_platforms JSON COMMENT '投放平台数组',
    schedule_config JSON NOT NULL COMMENT '定时配置：周几、时分秒、每天等',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用，2-已完成',
    user_id BIGINT NOT NULL COMMENT '关联用户',
    is_del TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_is_del (is_del)
);
```

#### 5.2 任务执行记录表 (task_execution_logs)

```sql
CREATE TABLE task_execution_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id BIGINT NOT NULL,
    execution_time TIMESTAMP NOT NULL COMMENT '执行时间',
    execution_content TEXT COMMENT '执行内容',
    execution_status TINYINT DEFAULT 0 COMMENT '执行状态：0-待确认，1-已确认，2-已取消',
    execution_result TEXT COMMENT '执行结果',
    confirmed_by BIGINT COMMENT '确认人',
    confirmed_time TIMESTAMP NULL COMMENT '确认时间',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (confirmed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_task_id (task_id),
    INDEX idx_execution_time (execution_time)
);
```

### 6. 平台规则模块

#### 6.1 平台规则表 (platform_rules)

```sql
CREATE TABLE platform_rules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    platform_type ENUM('xiaohongshu', 'douyin', 'wechat_video', 'general') NOT NULL COMMENT '所属平台',
    rule_content LONGTEXT NOT NULL COMMENT '规则内容',
    rule_category VARCHAR(50) COMMENT '规则分类',
    priority INT DEFAULT 0 COMMENT '优先级',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by BIGINT NOT NULL COMMENT '创建人',
    is_del TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_platform_type (platform_type),
    INDEX idx_created_by (created_by),
    INDEX idx_is_del (is_del)
);
```
