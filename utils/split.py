import cv2
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt

class ImageSplitter:
    """
    自动切分PNG图片中的多个物件
    
    功能：
    1. 自动检测白底PNG中的彩色物件
    2. 使用连通区域分析算法识别每个独立物件
    3. 计算每个物件的精确边界框
    4. 保存每个物件为单独的PNG文件
    """
    
    def __init__(self, tolerance=20, min_area=100):
        """
        初始化分割器
        
        参数:
        tolerance: 背景颜色容忍度 (0-255)
        min_area: 最小区域面积，小于此值的噪点会被过滤
        """
        self.tolerance = tolerance
        self.min_area = min_area
        
    def load_image(self, image_path):
        """加载图片并转换为OpenCV格式"""
        # 使用PIL加载图片，保留透明度通道
        pil_image = Image.open(image_path)
        
        # 转换为RGBA格式（如果有透明度）
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
            
        # 转换为numpy数组
        image_np = np.array(pil_image)
        
        # 转换为BGR格式供OpenCV使用
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGRA)
        
        return image_cv, pil_image
    
    def is_background_color(self, pixel, bg_color, tolerance):
        """判断像素是否为背景色"""
        # 对于RGBA图像，我们检查颜色通道
        if len(pixel) >= 3:
            # 计算颜色差异（欧几里得距离）
            diff = np.sqrt(
                (int(pixel[0]) - bg_color[0])**2 +
                (int(pixel[1]) - bg_color[1])**2 +
                (int(pixel[2]) - bg_color[2])**2
            )
            return diff <= tolerance
            
        return False
    
    def find_background_color(self, image_cv):
        """自动检测背景色（假设为图像四个角的颜色）"""
        height, width = image_cv.shape[:2]
        
        # 获取四个角的像素
        corners = [
            image_cv[0, 0],           # 左上角
            image_cv[0, width-1],     # 右上角
            image_cv[height-1, 0],    # 左下角
            image_cv[height-1, width-1]  # 右下角
        ]
        
        # 计算平均颜色
        corners_array = np.array(corners)
        avg_color = np.mean(corners_array[:, :3], axis=0).astype(int)
        
        return avg_color.tolist()
    
    def create_mask(self, image_cv):
        """创建前景掩码（非背景区域）"""
        # 检测背景色
        bg_color = self.find_background_color(image_cv)
        
        # 创建掩码
        height, width = image_cv.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # 遍历每个像素，标记非背景区域
        for y in range(height):
            for x in range(width):
                pixel = image_cv[y, x]
                if not self.is_background_color(pixel, bg_color, self.tolerance):
                    mask[y, x] = 255
        
        return mask
    
    def find_connected_components(self, mask):
        """使用OpenCV的连通组件分析找到所有独立区域"""
        # 寻找连通区域
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=8, ltype=cv2.CV_32S
        )
        
        # 过滤掉背景（第一个标签是背景）和太小的区域
        components = []
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= self.min_area:
                # 获取边界框
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                
                components.append({
                    'id': i,
                    'area': area,
                    'bbox': (x, y, w, h),
                    'centroid': (int(centroids[i][0]), int(centroids[i][1]))
                })
        
        return components, labels
    
    def extract_sub_images(self, image_cv, components):
        """提取每个组件为独立的图片"""
        sub_images = []
        
        for i, comp in enumerate(components):
            x, y, w, h = comp['bbox']
            
            # 提取子图像（包括透明度）
            sub_image = image_cv[y:y+h, x:x+w]
            
            # 创建透明背景（如果原始图像没有透明度）
            if sub_image.shape[2] == 3:
                # 添加alpha通道
                sub_image = cv2.cvtColor(sub_image, cv2.COLOR_BGR2BGRA)
            
            sub_images.append({
                'image': sub_image,
                'bbox': comp['bbox'],
                'id': comp['id'],
                'index': i
            })
        
        return sub_images
    
    def save_sub_images(self, sub_images, output_dir, base_filename):
        """保存所有子图像到指定目录"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        saved_files = []
        
        for item in sub_images:
            # 生成文件名
            filename = f"{base_filename}_{item['index']:03d}.png"
            filepath = os.path.join(output_dir, filename)
            
            # 保存图片
            cv2.imwrite(filepath, item['image'])
            saved_files.append(filepath)
            
            print(f"已保存: {filename} (区域 {item['id']}, 位置: {item['bbox']})")
        
        return saved_files
    
    def visualize_results(self, image_cv, components, mask, output_path=None):
        """可视化分割结果"""
        # 创建可视化图像
        vis_image = image_cv.copy()
        
        # 绘制边界框
        for comp in components:
            x, y, w, h = comp['bbox']
            # 绘制绿色矩形框
            cv2.rectangle(vis_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # 绘制区域ID
            cv2.putText(vis_image, str(comp['id']), (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 保存或显示结果
        if output_path:
            cv2.imwrite(output_path, vis_image)
            print(f"可视化结果已保存到: {output_path}")
        
        return vis_image
    
    def split_image(self, image_path, output_dir="./output", 
                    visualize=True, save_individual=True):
        """
        主函数：分割图片
        
        参数:
        image_path: 输入图片路径
        output_dir: 输出目录
        visualize: 是否生成可视化结果
        save_individual: 是否保存单独的切图
        
        返回:
        分割结果的字典
        """
        print(f"正在处理图片: {image_path}")
        
        # 1. 加载图片
        image_cv, pil_image = self.load_image(image_path)
        print(f"图片尺寸: {image_cv.shape[1]}x{image_cv.shape[0]}")
        
        # 2. 创建掩码
        mask = self.create_mask(image_cv)
        print(f"前景像素数: {np.sum(mask > 0)}")
        
        # 3. 寻找连通组件
        components, labels = self.find_connected_components(mask)
        print(f"找到 {len(components)} 个独立物件")
        
        # 4. 提取子图像
        sub_images = self.extract_sub_images(image_cv, components)
        
        # 5. 保存结果
        saved_files = []
        if save_individual:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            saved_files = self.save_sub_images(sub_images, output_dir, base_name)
        
        # 6. 可视化
        vis_image = None
        if visualize:
            vis_path = os.path.join(output_dir, "visualization.png")
            vis_image = self.visualize_results(image_cv, components, mask, vis_path)
        
        # 返回结果
        return {
            'original_image': image_cv,
            'mask': mask,
            'components': components,
            'sub_images': sub_images,
            'saved_files': saved_files,
            'visualization': vis_image,
            'count': len(components)
        }


# ==================== 示例使用 ====================

def example_usage():
    """示例使用代码"""
    
    # 创建分割器实例
    splitter = ImageSplitter(
        tolerance=30,      # 背景颜色容忍度
        min_area=50        # 最小区域面积（过滤噪点）
    )
    
    # 注意：这里使用一个示例图片路径
    # 实际使用时，请将下面的路径替换为您的图片路径
    test_image_path = "./assets/items/items.png"
    
    # 检查图片是否存在，如果不存在则创建一个示例图片用于演示
    if not os.path.exists(test_image_path):
        print("未找到测试图片，创建示例图片...")
        create_sample_image(test_image_path)
    
    # 执行分割
    result = splitter.split_image(
        image_path=test_image_path,
        output_dir="./split_results",
        visualize=True,
        save_individual=True
    )
    
    print(f"\n处理完成！共分割出 {result['count']} 个物件。")
    print(f"结果保存在: ./split_results/")
    
    return result


def create_sample_image(output_path):
    """创建一个示例测试图片（白底上有多个彩色物件）"""
    from PIL import Image, ImageDraw
    
    # 创建一个白色背景的图像
    width, height = 400, 300
    image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 绘制几个简单的图形作为测试物件
    colors = [
        (255, 0, 0, 255),    # 红色
        (0, 255, 0, 255),    # 绿色
        (0, 0, 255, 255),    # 蓝色
        (255, 255, 0, 255),  # 黄色
        (255, 0, 255, 255),  # 紫色
    ]
    
    # 绘制圆形
    draw.ellipse((20, 20, 120, 120), fill=colors[0])
    
    # 绘制矩形
    draw.rectangle((150, 30, 250, 130), fill=colors[1])
    
    # 绘制三角形
    draw.polygon([(300, 30), (350, 130), (250, 130)], fill=colors[2])
    
    # 绘制星形
    draw.regular_polygon((100, 200, 40), n_sides=5, fill=colors[3])
    
    # 绘制另一个圆形
    draw.ellipse((200, 180, 280, 260), fill=colors[4])
    
    # 保存图片
    image.save(output_path)
    print(f"示例图片已创建: {output_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("PNG自动切图工具")
    print("功能: 自动分割白底PNG中的多个独立物件")
    print("=" * 60)
    
    # 运行示例
    example_usage()
    
    print("\n提示:")
    print("1. 若要处理自己的图片，请修改 example_usage() 中的 test_image_path")
    print("2. 调整 tolerance 参数可以改变背景识别的灵敏度")
    print("3. 调整 min_area 参数可以过滤小噪点")


if __name__ == "__main__":
    main()
