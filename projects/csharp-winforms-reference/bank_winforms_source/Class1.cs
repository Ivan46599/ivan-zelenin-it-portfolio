using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WindowsFormsApp6
{

    class Client
    {
        public string lastname;
        public string firstname;
        public string surname;
        public string card_number;
        public string telephone_number;
        public string passport_number;
        public string passport_series;
        public DateTime chande_time;
        public string what_was_chande;
        public string who_was_chande;

        public void setTelephone_number(string filename)
        {
            telephone_number = filename;
        }
        public string getTelephone_number()
        {
            return telephone_number;
        }

        public void setCard_number(string filename)
        {
            card_number = filename;
        }
        public string getCard_number()
        {
            return card_number;
        }
        public void setСhande_time(DateTime filename)
        {
            chande_time = filename;
        }
        public DateTime getСhande_time()
        {
            return chande_time;
        }

        public void setWhat_was_chande(string filename)
        {
            what_was_chande = filename;
        }
        public string getWhat_was_chande()
        {
            return what_was_chande;
        }
        public void setWho_was_chande(string filename)
        {
            who_was_chande = filename;
        }
        public string getWho_was_chande()
        {
            return who_was_chande;
        }
        public void setPassport_number(string filename)
        {
            passport_number = filename;
        }
        public string getPassport_number()
        {
            return passport_number;
        }

        public void setPassport_series(string filename)
        {
            passport_series = filename;
        }
        public string getPassport_series()
        {
            return passport_series;
        }

        public void setLastname(string filename)
        {
            lastname = filename;
        }
        public string getLastname()
        {
            return lastname;
        }

        public void setFirstname(string filename)
        {
            firstname = filename;
        }
        public string getFirstname()
        {
            return firstname;
        }

        public void setSurname(string filename)
        {
            surname = filename;
        }
        public string getSurname()
        {
            return surname;
        }

        public string MaskedPassportInfo()
        {
            if (string.IsNullOrEmpty(passport_number))
                return string.Empty;
            else
                return "*****";
        }
        public string MaskedPassportInfo2()
        {
            if (string.IsNullOrEmpty(passport_series))
                return string.Empty;
            else
                return "*****";
        }

        public string GetMaskedBankCardNumber()
        {

            if (string.IsNullOrEmpty(card_number))
                return string.Empty;
            else
                return "******************";
        }

        public string Info()
        {
            string s = lastname + " " + firstname + " " + surname + " " + telephone_number + " " + passport_series + " " + passport_number
                + " " + chande_time + " " + what_was_chande + " " + who_was_chande;
            return s;
        }
        private string Encrypt(string plaintext, int shift)///// переделать!!!
        {
            StringBuilder ciphertext = new StringBuilder();
            foreach (char c in plaintext)
            {
                if (char.IsLetter(c))
                {
                    char base_char = char.IsUpper(c) ? 'A' : 'a';
                    ciphertext.Append((char)((c - base_char + shift) % 26 + base_char));
                }
                else
                {
                    ciphertext.Append(c);
                }
            }
            return ciphertext.ToString();
        }

        private string Decrypt(string ciphertext, int shift)///// переделать!!!
        {
            return Encrypt(ciphertext, 26 - shift);
        }

        public void SaveToFile(string filePath)///// переделать!!!
        {
            using (StreamWriter writer = new StreamWriter(filePath))
            {
                writer.WriteLine($"Lastname: {lastname}");
                writer.WriteLine($"Firstname: {firstname}");
                writer.WriteLine($"Surname: {surname}");
                writer.WriteLine($"Card Number: {card_number}");
                writer.WriteLine($"Telephone Number: {telephone_number}");
                writer.WriteLine($"Passport Number: {passport_number}");
                writer.WriteLine($"Passport Series: {passport_series}");

            }
        }
    }

    class salaryClient : Client
    {
        public string company;
        public void getCompany(string filename)
        {
            company = filename;
        }
        public string getCompany()
        {
            return company;
        }
        public string newInfo()
        {
            string s = lastname + " " + firstname + " " + surname + " " + company ;
            return s;
        }
        public salaryClient (string lastname, string firstname, string surname, string company)
        {
            this.lastname = lastname;
            this.firstname = firstname;
            this.surname = surname;
            this.company = company;
        }
        public void newSaveToFile(string filePath)
        {
            using (StreamWriter writer = new StreamWriter(filePath))
            {
                writer.WriteLine($"Lastname: {lastname}");
                writer.WriteLine($"Firstname: {firstname}");
                writer.WriteLine($"Surname: {surname}");
                writer.WriteLine($"Company: {company}");
                
            }
        }
    }
}


 
