using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp6
{
    class Senior_manager : Manager
    {
        public new String Role = "Старший менеджер";
        public DataGridView Customize_Data_Grid_View_for_Senior_manager(DataGridView dataGridView1)
        {
            // Ограничение возможности редактирования ячеек
            // Для Старшего Менеджера все доступно к редактированию

            return dataGridView1;
        }
        public new DataGridView Get_Data_Grid_View(DataGridView dataGridView1)
        {
            DataTable dt;
            dt = Get_Data_Table();
            dataGridView1.DataSource = dt;
            dataGridView1 = Customize_Data_Grid_View_for_Senior_manager(dataGridView1);
            return dataGridView1;
        }

    }
}
