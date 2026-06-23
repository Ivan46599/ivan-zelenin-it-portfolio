using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp6
{
    class Manager : Consultant
    {
        public new String Role = "Менеджер";
        public DataGridView Customize_Data_Grid_View_for_Manager(DataGridView dataGridView1)
        {
            // Ограничение возможности редактирования ячеек
            // Для Менеджера не доступна к редактированию только колонка "Номер карты"
            // Заменяем значение на ***
            for (int i = 0; i < dataGridView1.Rows.Count; i++)
                {
                    dataGridView1.Rows[i].Cells["Номер карты"].Value = "******************";
                    dataGridView1.Rows[i].Cells["Номер карты"].ReadOnly = true;
                }
            return dataGridView1;
        }
        public new DataGridView Get_Data_Grid_View(DataGridView dataGridView1)
        {
            DataTable dt;
            dt = Get_Data_Table();
            dataGridView1.DataSource = dt;
            dataGridView1 = Customize_Data_Grid_View_for_Manager(dataGridView1);
            return dataGridView1;
        }
    }
}
