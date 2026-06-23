using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace vodznak1
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog openFileDialog = new OpenFileDialog())
            {
                openFileDialog.Filter = "Images|*.bmp;*.jpg;*.jpeg;*.png";
                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    pictureBox1.Image = new Bitmap(openFileDialog.FileName);
                }
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (pictureBox1.Image != null)
            {
                // Получение размеров изображения
                int width = pictureBox1.Image.Width;
                int height = pictureBox1.Image.Height;

                Bitmap originalImage = (Bitmap)pictureBox1.Image;
                Bitmap watermarkImage = ExtractWatermark(originalImage);
                pictureBox2.Image = watermarkImage;// Отображение изображения с водяным знаком
            }
            else
            {
                MessageBox.Show("загрузите изображение");
            }
        }
        private Bitmap ExtractWatermark(Bitmap image)
        {
            int width = image.Width;
            int height = image.Height;
            
            // Создание нового изображения для водяного знака
            Bitmap watermark = new Bitmap(width, height);

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = image.GetPixel(x, y);
                    
                    // Извлечение двух наименее значимых битов для каждого канала
                    int red = (pixel.R & 0b00000011); // используются два LSB красного
                    int green = (pixel.G & 0b00000011); // два LSB зеленого
                    int blue = (pixel.B & 0b00000011); // два LSB синего

                    red = (red << 6);   // смещение на 6, чтобы заполнить 8 бит
                    green = (green << 6);
                    blue = (blue << 6);


                    Color watermarkPixelColor = Color.FromArgb(red, green, blue);
                    watermark.SetPixel(x, y, watermarkPixelColor);

                    //watermark.SetPixel(x, y, Color.FromArgb(red, green, blue));// Формирование пикселя для водяного знака

                }
            }

            return watermark;
        }
    }
}
    

