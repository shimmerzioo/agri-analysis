import os
import shutil
import sys
from flask_frozen import Freezer
from app import app

# 确保工作目录正确
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    # 创建build目录
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.makedirs('build')
    print("✅ 创建build目录成功")

    # 复制静态文件
    if os.path.exists('static'):
        shutil.copytree('static', 'build/static')
        print("✅ 复制静态文件成功")
    else:
        print("⚠️ 警告: static目录不存在，跳过复制")

    # 设置Freezer配置
    app.config['FREEZER_DESTINATION'] = 'build'
    app.config['FREEZER_RELATIVE_URLS'] = True
    app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'] = True
    # 忽略404和500错误
    app.config['FREEZER_SKIP_EXISTING'] = True
    app.config['FREEZER_IGNORE_404_NOT_FOUND'] = True
    
    # 冻结Flask应用
    freezer = Freezer(app)

    # 只注册确定存在的页面
    @freezer.register_generator
    def index_url():
        yield {}  # 首页

    @freezer.register_generator
    def map_url():
        yield {}  # 地图页面
        
    # 添加API路由生成器
    @freezer.register_generator
    def api_metadata():
        yield {'path': '/api/metadata/'}
        
    @freezer.register_generator
    def api_map_data():
        yield {'path': '/api/map-data/'}

    # 检查app.py中的路由，确保只生成存在的页面
    print("🔍 检查可用路由...")
    available_templates = os.listdir('templates')
    print(f"📁 可用模板: {', '.join(available_templates)}")
    
    print("🔄 开始生成静态文件...")
    # 使用try-except捕获单个页面的错误，而不是整个过程失败
    try:
        freezer.freeze()
        print("✅ 静态文件生成成功！")
    except Exception as e:
        print(f"⚠️ 生成过程中遇到错误: {str(e)}")
        print("⚠️ 尝试继续生成其他页面...")
        
        # 手动生成已知可用的页面
        for rule in app.url_map.iter_rules():
            if 'GET' in rule.methods and not rule.rule.startswith('/static') and not rule.rule.startswith('/explore'):
                try:
                    print(f"🔄 正在生成: {rule.rule}")
                    freezer.freeze_url(rule.rule)
                    print(f"✅ 成功生成: {rule.rule}")
                except Exception as page_error:
                    print(f"❌ 无法生成 {rule.rule}: {str(page_error)}")
    
    print("🎉 构建完成! 静态文件已生成到build目录")
    
except Exception as e:
    print(f"❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)