# 执行：在项目根目录运行 `powershell -ExecutionPolicy Bypass -File .\scripts\replace-step21-title.ps1`

$new = 'Remove unnecessary parts from the servo'

Get-ChildItem -Path (Resolve-Path ..\) -Recurse -Include *.html | ForEach-Object {
    $path = $_.FullName
    $text = Get-Content -Path $path -Raw -Encoding UTF8
    $updated = $text

    # 1) 将 "Step 21: ..." 行内容替换为目标文本（保留 "Step 21:" 前缀）
    $updated = [Regex]::Replace($updated, '(?mi)(Step\s*21\s*:\s*)([^\r\n<]+)', '$1' + $new)

    # 2) 将侧栏或其他以 "21: ..." 开头的纯文本（例如 <a>21: ...</a>）替换
    $updated = [Regex]::Replace($updated, '(?mi)(>21:\s*)([^<]+)(<)', '$1' + $new + '$3')

    # 3) 直接替换常见的原始标题短语（大小写不敏感）
    $updated = [Regex]::Replace($updated, '(?mi)Spool Assembly and Servo Connection', $new)
    $updated = [Regex]::Replace($updated, '(?mi)Spool assembly and attaching to servo', $new)
    $updated = [Regex]::Replace($updated, '(?mi)Spool Assembly and attaching to servo', $new)

    if ($updated -ne $text) {
        Set-Content -Path $path -Value $updated -Encoding UTF8
        Write-Host "Updated: $path"
    }
}
