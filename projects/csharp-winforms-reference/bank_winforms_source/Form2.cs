using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
namespace WindowsFormsApp6
{
    public partial class Form2 : Form
    {
        string file_name = "data.txt";

        public Form2()
        {
            InitializeComponent();

        }
        private void Form2_load(object sender, EventArgs e)
        {
            if (Program.User_Role != null) { role_lable.Text = Program.User_Role; }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (File.Exists(file_name))
            {
                Form3 f = new Form3();
                f.Show();
                this.Hide();
            }
            else
            {
                MessageBox.Show("Файла нет");
                return;
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            this.Hide();
        }

    }
}
