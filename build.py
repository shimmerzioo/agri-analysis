import os
import shutil
from flask_frozen import Freezer
from app import app

# 创建build目录
if os.path.exists('build'):
    shutil.rmtree('build')
os.makedirs('build')

# 复制静态文件
if os.path.exists('static'):
    shutil.copytree('static', 'build/static')

# 冻结Flask应用
freezer = Freezer(app)

@freezer.register_generator
def index_url():
    yield {}

@freezer.register_generator
def map_url():
    yield {}

if __name__ == '__main__':
    freezer.freeze()