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
    public partial class Form3 : Form
    {
        public Form3()
        {
            InitializeComponent();
        }

        private void Form3_Load(object sender, EventArgs e)
        {
            if (File.Exists(Program.File_path)) { } else MessageBox.Show("Нет файла с данными");
            role_lable.Text = Program.User_Role;
            switch (Program.User_Role)
            {
                case "Консультант":
                    Consultant Kons = new Consultant();
                    dataGridView1 = Kons.Get_Data_Grid_View(dataGridView1);
                    break;
                case "Менеджер":
                    Manager Manager = new Manager();
                    dataGridView1 = Manager.Get_Data_Grid_View(dataGridView1);
                    break;
                case "Старший менеджер":
                    Senior_manager Senior_manager = new Senior_manager();
                    dataGridView1 = Senior_manager.Get_Data_Grid_View(dataGridView1);
                    break;
            }
            dataGridView1.AutoResizeColumns();
        }
        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }
        private void button_save_Click(object sender, EventArgs e)
        {

            var cipher = new CaesarCipher();


            StreamWriter sw = new StreamWriter(Program.File_path);
            int nul_line = 0;
            String st_line = "";
            for (int i = 0; i < dataGridView1.RowCount; i++)
            {
                for (int j = 0; j < dataGridView1.ColumnCount; j++)
                {
                    if (dataGridView1.Rows[i].Cells[j].Value == null)
                    {
                        st_line = st_line + "null";
                        nul_line++;
                    }
                    else
                    {
                        var encryptedText = cipher.Encrypt(dataGridView1.Rows[i].Cells[j].Value.ToString(), 2);
                        st_line = st_line + encryptedText;
                    }
                    if (j < dataGridView1.ColumnCount - 1)
                    {
                        st_line = st_line + " ";
                        // не пишем пробел после последней колонки
                    }
                }
                if (nul_line != dataGridView1.ColumnCount) sw.WriteLine(st_line);
                //sw.WriteLine();
                st_line = "";
            }
            sw.Close();
            MessageBox.Show("Сохранено");
        }

    }
}
