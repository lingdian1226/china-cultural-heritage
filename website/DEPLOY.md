# 部署说明 - 全国重点文物保护单位查询系统

## Nginx 配置

在现有 nginx 配置中添加以下 location 块，将网站部署到 `/heritage/` 路径：

```nginx
server {
    # ... 你现有的博客配置 ...

    # 文物保护单位查询系统
    location /heritage/ {
        alias /var/www/heritage/;
        index index.html;
        try_files $uri $uri/ /heritage/index.html;
        
        # 静态资源缓存
        location ~* \.(css|js)$ {
            expires 7d;
            add_header Cache-Control "public, immutable";
        }
        
        # data.js 文件较大，启用 gzip
        gzip on;
        gzip_types application/javascript text/css;
        gzip_min_length 1024;
    }
}
```

## 部署步骤

1. **构建数据文件**
   ```bash
   cd /root/.openclaw/workspace/china-cultural-heritage
   python3 build.py
   ```

2. **复制文件到 Web 目录**
   ```bash
   sudo mkdir -p /var/www/heritage
   sudo cp website/* /var/www/heritage/
   ```

3. **测试 nginx 配置**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **访问**
   打开 `http://your-domain/heritage/`

## 文件说明

| 文件 | 说明 | 大小 |
|------|------|------|
| `index.html` | 主页面 | ~4 KB |
| `style.css` | 样式表 | ~9 KB |
| `app.js` | 应用逻辑 | ~15 KB |
| `data.js` | 数据文件 | ~1.5 MB |

## 注意事项

- `data.js` 文件较大（约 1.5 MB），建议确保 nginx 已启用 gzip 压缩
- 网站为纯静态 SPA，无需后端服务
- 所有外部依赖（Chart.js）通过 CDN 加载
