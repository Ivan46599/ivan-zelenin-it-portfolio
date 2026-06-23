using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp6
{
    class Consultant
    {
        public String Role = "Консультант";
        public DataTable Get_Data_Table()
        {
            DataTable dt;
            dt = new DataTable();
            dt.Columns.Add("Фамилия");
            dt.Columns.Add("Имя");
            dt.Columns.Add("Отчество");
            dt.Columns.Add("Номер карты");
            dt.Columns.Add("Номер телефона");
            dt.Columns.Add("Номер паспорта");
            dt.Columns.Add("Серия Паспорта");

            if (File.Exists(Program.File_path))
            {

                var cipher = new CaesarCipher();


                StreamReader file = new StreamReader(Program.File_path);
                string[] values;
                string newline;

                while ((newline = file.ReadLine()) != null)
                {
                    DataRow dr = dt.NewRow();
                    values = newline.Split(' ');

                    dr[0] = cipher.Decrypt(values[0], 2);
                    dr[1] = cipher.Decrypt(values[1], 2);
                    dr[2] = cipher.Decrypt(values[2], 2);
                    dr[3] = cipher.Decrypt(values[3], 2);
                    dr[4] = cipher.Decrypt(values[4], 2);
                    dr[5] = cipher.Decrypt(values[5], 2);
                    dr[6] = cipher.Decrypt(values[6], 2);
                    dt.Rows.Add(dr);
                }
                file.Close();
            }

            return dt;
        }
        public DataGridView Customize_Data_Grid_View_for_Konsultant(DataGridView dataGridView1)
        {
            // Ограничение возможности редактирования ячеек
            // Для консультанта доступна к редактированию только колонка "Номер телефона"
            // Заменяем значение на ***
            for (int i = 0; i < dataGridView1.Rows.Count; i++)
                {
                    dataGridView1.Rows[i].Cells["Фамилия"].ReadOnly = true;
                    dataGridView1.Rows[i].Cells["Имя"].ReadOnly = true;
                    dataGridView1.Rows[i].Cells["Отчество"].ReadOnly = true;
                    dataGridView1.Rows[i].Cells["Номер карты"].ReadOnly = true;
                    dataGridView1.Rows[i].Cells["Номер паспорта"].ReadOnly = true;
                    dataGridView1.Rows[i].Cells["Серия паспорта"].ReadOnly = true;
                    dataGridView1.Rows[i].Cells["Номер карты"].Value = "******************";
                    dataGridView1.Rows[i].Cells["Номер паспорта"].Value = "******************";
                    dataGridView1.Rows[i].Cells["Серия паспорта"].Value = "******************";

            }


            // Ограничение возможности добавления новых записей (Для консультанта заблокировано)
            dataGridView1.AllowUserToAddRows = false;

            return dataGridView1;

        }
        public DataGridView Get_Data_Grid_View(DataGridView dataGridView1)
        {
            DataTable dt;
            dt = Get_Data_Table();
            dataGridView1.DataSource = dt;
            dataGridView1 = Customize_Data_Grid_View_for_Konsultant(dataGridView1);


            return dataGridView1;
        }
        public void Save_DGV_to_txt(DataGridView dataGridView1)
        {
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
                        st_line = st_line + dataGridView1.Rows[i].Cells[j].Value.ToString();
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
        }
    }


}
