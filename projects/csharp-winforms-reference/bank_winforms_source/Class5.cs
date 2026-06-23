using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.LinkLabel;

namespace WindowsFormsApp6
{
    class Save
    {

        public void SaveClientsToFile(object sender, EventArgs e)
        {
            Client client1 = new Client
            {
                lastname = "Иванов",
                firstname = "Иван",
                surname = "Иванович",
                card_number = "1234567890",
                telephone_number = "123456789",
                passport_number = "987654321",
                passport_series = "3456",

            };

            Client client2 = new Client
            {
                lastname = "Петров",
                firstname = "Петр",
                surname = "Петрович",
                card_number = "0987654321",
                telephone_number = "987654321",
                passport_number = "123456789",
                passport_series = "3490",

            };
            string filePath = @"C:\CLIENT\client.txt";
            try
            {
                using (StreamWriter streamWriter = new StreamWriter(filePath, true))
                {
                    streamWriter.WriteLine(client1.Info());
                    streamWriter.WriteLine(client2.Info());
                }
                MessageBox.Show("Клиенты сохранены в файл.");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка при сохранении файла: {ex.Message}");
            }
        }

        private void EnsureClientDirectory()
        {
            string path = @"C:\CLIENT";
            DirectoryInfo dirInfo = new DirectoryInfo(path);
            if (!dirInfo.Exists)
            {
                dirInfo.Create();
                MessageBox.Show(@"Create dir C:\STUDENT");
            }
        }
    }
}

