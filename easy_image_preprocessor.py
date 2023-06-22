import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import ntpath
import threading
import configparser

class ImagePreprocessor:
    def __init__(self, size=(512, 512), file_format='PNG', quality=95, base_name='image'):
        self.size = size
        self.file_format = file_format
        self.quality = quality
        self.base_name = base_name

    def preprocess_image(self, image_path):
        try:
            image = Image.open(image_path)
        except IOError:
            print(f'Error opening image {image_path}. Please check if the file is an image.')
            return None
        except Exception as e:
            print(f'An unexpected error occurred while opening image {image_path}: {e}')
            return None
        return image.resize(self.size, Image.ANTIALIAS)

    def save_image(self, image, save_path):
        if image:
            try:
                if self.file_format == 'JPEG':
                    image.save(save_path, self.file_format, quality=self.quality)
                else:
                    image.save(save_path, self.file_format)
            except IOError:
                print(f'Error saving image {save_path}. Please check the destination path.')
                return False
            except Exception as e:
                print(f'An unexpected error occurred while saving image {save_path}: {e}')
                return False
        return True

    def preprocess_images(self, source_folder, destination_folder, update_preview, update_result_preview, progress_label):
        """Preprocess images from source_folder and save them to destination_folder.

        Args:
            source_folder (str): Path to the source folder.
            destination_folder (str): Path to the destination folder.
        """
        if not os.path.exists(destination_folder):
            progress_label.config(text=f"Error creating directory {destination_folder}. Please check your permissions or the path.")
            return

        file_count = 1
        for dirpath, dirnames, filenames in os.walk(source_folder):
            for img_filename in filenames:
                source_path = os.path.join(dirpath, img_filename)
                dest_path = os.path.join(destination_folder, f'{self.base_name} ({file_count}).{self.file_format.lower()}')

                if os.path.isfile(source_path) and img_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
                    if not self.validate_image(source_path):
                        progress_label.config(text=f'Invalid image file encountered: {source_path}')
                        continue

                    update_preview(source_path)
                
                    preprocessed_img = self.preprocess_image(source_path)
                    if self.save_image(preprocessed_img, dest_path):
                        progress_label.config(text=f'Successfully preprocessed {source_path} to {dest_path}')
                        update_result_preview(preprocessed_img)
                        file_count += 1
                    else:
                        progress_label.config(text=f'Failed to save preprocessed image {source_path}.')
                else:
                    progress_label.config(text=f'Invalid image file encountered: {source_path}')
        progress_label.config(text="Image preprocessing completed.")
    def validate_image(self, image_path):
        try:
            Image.open(image_path).verify()
            return True
        except (IOError, SyntaxError):
            return False



def update_preview(image_path):
    if image_path:
        preview_image = Image.open(image_path)
        preview_image.thumbnail((256, 256))
        photo = ImageTk.PhotoImage(preview_image)
        preview_label.config(image=photo)
        preview_label.image = photo

def update_result_preview(image):
    result_image = image.copy()
    result_image.thumbnail((256, 256))
    photo = ImageTk.PhotoImage(result_image)
    result_preview_label.config(image=photo)
    result_preview_label.image = photo

def browse_src_folder():
    src_folder = filedialog.askdirectory()
    src_folder_path.set(src_folder)

def browse_dest_folder():
    dest_folder = filedialog.askdirectory()
    dest_folder_path.set(dest_folder)

def process_images():
    preprocessor = ImagePreprocessor(size=(int(width_entry.get()), int(height_entry.get())), file_format=output_format.get(), quality=int(quality_scale.get()), base_name=base_name_entry.get())
    
    process_thread = threading.Thread(target=preprocessor.preprocess_images, args=(src_folder_path.get(), dest_folder_path.get(), update_preview, update_result_preview, progress_label))
    process_thread.start()

def save_preferences():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'SourceFolder': src_folder_path.get(),
        'DestinationFolder': dest_folder_path.get(),
        'OutputFormat': output_format.get(),
        'ImageWidth': image_width.get(),
        'ImageHeight': image_height.get(),
        'Quality': quality_scale.get(),
        'BaseName': base_name.get()
    }
    with open('preferences.ini', 'w') as configfile:
        config.write(configfile)

def load_preferences():
    config = configparser.ConfigParser()
    config.read('preferences.ini')
    default = config['DEFAULT']
    src_folder_path.set(default.get('SourceFolder', ''))
    dest_folder_path.set(default.get('DestinationFolder', ''))
    output_format.set(default.get('OutputFormat', 'PNG'))
    image_width.set(default.get('ImageWidth', '512'))
    image_height.set(default.get('ImageHeight', '512'))
    quality_scale.set(default.get('Quality', '95'))
    base_name.set(default.get('BaseName', 'image'))

def validate_image(self, image_path):
    try:
        Image.open(image_path).verify()
        return True
    except (IOError, SyntaxError):
        return False


app = Tk()
app.title("Image Preprocessor")

src_folder_path = StringVar()
dest_folder_path = StringVar()
output_format = StringVar(value='PNG')
image_width = StringVar(value='512')
image_height = StringVar(value='512')


base_name = StringVar(value='image')
Label(app, text="Base name:").grid(row=5, column=0, sticky=W)
base_name_entry = Entry(app, textvariable=base_name, width=20)
base_name_entry.grid(row=5, column=1, sticky=W)


Label(app, text="Source folder:").grid(row=0, column=0, sticky=W)
Entry(app, textvariable=src_folder_path, width=50).grid(row=0, column=1)
Button(app, text="Browse", command=browse_src_folder).grid(row=0, column=2)
Label(app, text="Destination folder:").grid(row=1, column=0, sticky=W)
Entry(app, textvariable=dest_folder_path, width=50).grid(row=1, column=1)
Button(app, text="Browse", command=browse_dest_folder).grid(row=1, column=2)
progress_label = Label(app, text="")
progress_label.grid(row=8, column=0, sticky=W, columnspan=3)

Label(app, text="Output format:").grid(row=2, column=0, sticky=W)
Radiobutton(app, text="PNG", variable=output_format, value="PNG").grid(row=2, column=1, sticky=W)
Radiobutton(app, text="JPEG", variable=output_format, value="JPEG").grid(row=2, column=1, sticky=E)

Label(app, text="Resize dimensions:").grid(row=3, column=0, sticky=W)
width_entry = Entry(app, textvariable=image_width, width=6)
width_entry.grid(row=3, column=1, sticky=W)
Label(app, text="x").grid(row=3, column=1)
height_entry = Entry(app, textvariable=image_height, width=6)
height_entry.grid(row=3, column=1, sticky=E)

Label(app, text="JPEG quality:").grid(row=4, column=0, sticky=W)
quality_scale = Scale(app, from_=1, to=100, orient=HORIZONTAL, length=200)
quality_scale.set(95)
quality_scale.grid(row=4, column=1, sticky=W)

Button(app, text="Process Images", command=process_images).grid(row=7, column=0, pady=10)
Button(app, text="Save Preferences", command=save_preferences).grid(row=9, column=0, pady=10)
Button(app, text="Load Preferences", command=load_preferences).grid(row=9, column=1, pady=10)


Label(app, text="Original Image Preview:").grid(row=6, column=0, sticky=W)
preview_label = Label(app)
preview_label.grid(row=7, column=0, padx=5)

Label(app, text="Result Image Preview:").grid(row=6, column=1, sticky=W)
result_preview_label = Label(app)
result_preview_label.grid(row=7, column=1, padx=5)

app.mainloop()
