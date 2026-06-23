using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp6
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
            Form2 f = new Form2();
            Program.User_Role = "Консультант";
            f.Show();

        }

        private void button2_Click(object sender, EventArgs e)
        {
            Form2 f = new Form2();
            Program.User_Role = "Менеджер";
            f.Show();

        }

        private void button3_Click(object sender, EventArgs e)
        {
            Form2 f = new Form2();
            Program.User_Role = "Старший менеджер";
            f.Show();


        }
    }
}
