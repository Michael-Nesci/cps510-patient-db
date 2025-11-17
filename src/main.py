import flet as ft
import sqlite3


def main(page: ft.Page):
    # connect_db()

    page.title = "Patient Health Records DBMS"
    page.scroll=ft.ScrollMode.AUTO
    page.window.height = 600
    page.window.width = 400
    main_menu(page)

def main_menu(page: ft.Page):
    update_text = ft.Text(value="Please select an option...", italic=True)
    def create_tables(e):
        con = sqlite3.connect("data.db")
        cur = con.cursor()
        cur.execute("""
                CREATE TABLE patient (
                    Patient_Id    INTEGER     PRIMARY KEY,
                    F_Name        VARCHAR2(15)   NOT NULL,
                    M_Initial     CHAR(1),
                    L_Name        VARCHAR2(15)   NOT NULL,
                    Sex           CHAR(1) CHECK (Sex IN ('M', 'F', 'X')),
                    Dob           DATE           NOT NULL,
                    Address       VARCHAR2(50),
                    Email         VARCHAR2(30) CHECK (Email LIKE '%@%.%'),
                    Phone_Num     VARCHAR2(12) CHECK (Phone_Num LIKE '___-___-____'),
                    Insurance     VARCHAR2(50)
                );
                    """)
        cur.execute("""
                    CREATE TABLE doctor (
                    Doctor_Id    INTEGER      PRIMARY KEY CHECK (Doctor_Id >= 10000),
                    F_Name       VARCHAR2(15)   NOT NULL,
                    L_Name       VARCHAR2(15)   NOT NULL,
                    Sex          CHAR(1) CHECK (Sex IN ('M', 'F', 'X')),
                    Extension    VARCHAR2(6),
                    Specialty    VARCHAR2(50),
                    Lang         VARCHAR2(50),
                    Status       VARCHAR2(8)    DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive'))
                );
                """)
        cur.execute("""
                CREATE TABLE booked (
                    Appointment_Date    DATE          NOT NULL,
                    Patient_Id          INTEGER   NOT NULL,
                    Doctor_Id           INTEGER   NOT NULL,
                    Appointment_Time    VARCHAR2(5)   NOT NULL CHECK(Appointment_Time LIKE '__:__'),
                    Reason              VARCHAR2(50),
                    CONSTRAINT pk_booked PRIMARY KEY (Patient_Id, Appointment_Date, Appointment_Time),
                    CONSTRAINT fk_booked_pid FOREIGN KEY (Patient_Id) REFERENCES patient(Patient_Id),
                    CONSTRAINT fk_booked_did FOREIGN KEY (Doctor_Id) REFERENCES doctor(Doctor_Id),
                    CONSTRAINT ck_multiday UNIQUE (Patient_Id, Doctor_Id, Appointment_Date),
                    CONSTRAINT ck_double_book_patient UNIQUE (Appointment_Date, Patient_Id, Appointment_Time),
                    CONSTRAINT ck_double_book_doctor UNIQUE (Appointment_Date, Doctor_Id, Appointment_Time)
                );
                """)
        cur.execute("""
                CREATE TABLE bill (
                    payer              VARCHAR2(255) NOT NULL,
                    status             VARCHAR2(6)   NOT NULL,
                    amount             NUMBER(10,2)  NOT NULL,
                    Appointment_Date   DATE          NOT NULL,
                    Patient_Id         INTEGER     NOT NULL,
                    Doctor_Id          INTEGER     NOT NULL,
                    CONSTRAINT pk_bill PRIMARY KEY (Appointment_Date, Doctor_Id, Patient_Id),
                    CONSTRAINT fk_bill_booked FOREIGN KEY (Appointment_Date, Patient_Id, Doctor_Id) 
                        REFERENCES booked(Appointment_Date, Patient_Id, Doctor_Id)
                );
                    """)
        cur.execute("""
                CREATE TABLE medical_procedure (
                    filepath           VARCHAR2(255),
                    procedure_type     VARCHAR2(9)   NOT NULL,
                    location           VARCHAR2(20)   NOT NULL,
                    procedure_summary  VARCHAR2(255),
                    Appointment_Date   DATE          NOT NULL,
                    Patient_Id         INTEGER   NOT NULL,
                    Doctor_Id          INTEGER   NOT NULL,
                    CONSTRAINT pk_medical_procedure PRIMARY KEY (procedure_type, Appointment_Date, Doctor_Id, Patient_Id),
                    CONSTRAINT fk_medical_procedure_booked FOREIGN KEY (Appointment_Date, Patient_Id, Doctor_Id) 
                        REFERENCES booked(Appointment_Date, Patient_Id, Doctor_Id)
                );
                    """)
        cur.execute("""
                CREATE TABLE drug (
                    DIN             NUMBER(10)      NOT NULL,
                    drug_name       VARCHAR2(30)    NOT NULL,
                    dosage          NUMBER(10, 2)   NOT NULL,
                    CONSTRAINT pk_drug PRIMARY KEY (DIN)
                );
            """)
        cur.execute("""
                CREATE TABLE prescription (
                    DIN               NUMBER(10)    NOT NULL,
                    med_count         NUMBER(5)     NOT NULL,
                    refills           NUMBER(5)     DEFAULT 0,
                    frequency         NUMBER(5)     NOT NULL,
                    Appointment_Date  DATE          NOT NULL,
                    Patient_Id        INTEGER     NOT NULL,
                    Doctor_Id         INTEGER     NOT NULL,
                    CONSTRAINT pk_prescription PRIMARY KEY (DIN, Appointment_Date, Doctor_Id, Patient_Id),
                    CONSTRAINT fk_prescription_booked FOREIGN KEY (Appointment_Date, Patient_Id, Doctor_Id) 
                        REFERENCES booked(Appointment_Date, Patient_Id, Doctor_Id),
                    CONSTRAINT fk_din FOREIGN KEY (DIN) REFERENCES drug(DIN)
                );
                    """)
        
        cur.execute("""
                CREATE TABLE diagnosis (
                    Code_System       VARCHAR2(10)  NOT NULL,
                    Code              VARCHAR2(10)  NOT NULL,
                    Diagnosis_Name    VARCHAR2(30)  NOT NULL UNIQUE,
                    Condition_Type    VARCHAR2(15)  NOT NULL,
                    CONSTRAINT pk_code PRIMARY KEY (Code_System, Code),
                    CONSTRAINT ck_code_system CHECK (Code_System IN ('DSM-5-TR', 'ICD-10', 'ICD-11'))
                );
                    """)
        
        cur.execute("""
                CREATE TABLE conditions (
                    Condition_Id    INTEGER PRIMARY KEY,
                    Patient_Id      INTEGER    NOT NULL,
                    Diagnosis_Name  VARCHAR2(30) NOT NULL,
                    Onset_Date      DATE         NOT NULL,
                    CONSTRAINT fk_conditions_patient FOREIGN KEY (Patient_Id) REFERENCES patient(Patient_Id),
                    CONSTRAINT fk_conditions_diagnosis FOREIGN KEY (Diagnosis_Name) REFERENCES code(Diagnosis_Name),
                    CONSTRAINT ck_duplicates1 UNIQUE (Patient_Id, Diagnosis_Name, Onset_Date),
                    CONSTRAINT ck_duplicates2 UNIQUE (Patient_Id, Condition_Id, Onset_Date)
                );
                    """)
        cur.execute("""
                CREATE TABLE condition_details (
                    Condition_Id      INTEGER   NOT NULL,
                    Patient_Id        INTEGER   NOT NULL,
                    Code_System       VARCHAR2(10),
                    Code              VARCHAR2(10),
                    Onset_Date        DATE,
                    Abatement_Date    DATE,
                    Clinical_Status   VARCHAR2(12)  DEFAULT 'active',
                    Severity          VARCHAR2(10),
                    Doctor_Id         INTEGER,
                    CONSTRAINT pk_condition_dets PRIMARY KEY (Condition_Id),
                    CONSTRAINT fk_condition_dets_base1 FOREIGN KEY (Condition_Id) REFERENCES conditions(Condition_Id),
                    CONSTRAINT fk_condition_dets_base FOREIGN KEY (Patient_Id, Condition_Id, Onset_Date) REFERENCES conditions(Patient_Id, Condition_Id, Onset_Date),
                    CONSTRAINT fk_condition_dets_code FOREIGN KEY (Code_System, Code) REFERENCES code(Code_System, Code),
                    CONSTRAINT fk_condition_dets_doctor FOREIGN KEY (Doctor_Id) REFERENCES doctor(Doctor_Id),
                    CONSTRAINT ck_conditions_status CHECK (Clinical_Status IN ('active','resolved','remission','unknown')),
                    CONSTRAINT ck_conditions_severity CHECK (Severity IN ('mild','moderate','severe','critical'))
                );
                    """)
        cur.execute("""
            CREATE TABLE chronic_condition (
                Condition_Id                  INTEGER NOT NULL,
                Is_Lifestyle_Modifiable       CHAR(1),
                Long_Term_Med_Required        CHAR(1),
                Follow_Up_Interval_Months     NUMBER(3),
                CONSTRAINT pk_chronic_condition PRIMARY KEY (Condition_Id),
                CONSTRAINT fk_chronic_condition_base FOREIGN KEY (Condition_Id) 
                    REFERENCES conditions(Condition_Id) ON DELETE CASCADE,
                CONSTRAINT ck_chronic_yn_check CHECK (
                    (Is_Lifestyle_Modifiable IN ('Y','N') OR Is_Lifestyle_Modifiable IS NULL)
                    AND (Long_Term_Med_Required IN ('Y','N') OR Long_Term_Med_Required IS NULL)
                ),
                CONSTRAINT ck_chronic_fu_check CHECK (Follow_Up_Interval_Months IS NULL OR Follow_Up_Interval_Months >= 0)
            );
            """)

        cur.execute("""
            CREATE TABLE infectious_condition (
                Condition_Id        INTEGER NOT NULL,
                Pathogen_Type       VARCHAR2(20),
                Isolation_Required  CHAR(1),
                CONSTRAINT pk_infectious_condition PRIMARY KEY (Condition_Id),
                CONSTRAINT fk_infectious_condition_base FOREIGN KEY (Condition_Id) 
                    REFERENCES conditions(Condition_Id) ON DELETE CASCADE,
                CONSTRAINT ck_infectious_pathogen CHECK (
                    Pathogen_Type IN ('virus','bacteria','fungus','parasite','unknown') 
                    OR Pathogen_Type IS NULL
                ),
                CONSTRAINT ck_infectious_yn_check CHECK (
                    (Isolation_Required IN ('Y','N') OR Isolation_Required IS NULL)
                )
            );
        """)
    
        cur.execute("""
            CREATE TABLE injury_condition (
                Condition_Id    INTEGER  NOT NULL,
                Injury_Type     VARCHAR2(20),
                Body_Site       VARCHAR2(120),
                Laterality      VARCHAR2(10),
                Cause           VARCHAR2(20),
                Date_Of_Injury  DATE,
                CONSTRAINT pk_injury_condition PRIMARY KEY (Condition_Id),
                CONSTRAINT fk_injury_condition_base FOREIGN KEY (Condition_Id) 
                    REFERENCES conditions(Condition_Id) ON DELETE CASCADE,
                CONSTRAINT ck_injury_laterality CHECK (
                    Laterality IN ('left','right','bilateral','midline','na') 
                    OR Laterality IS NULL
                )
            );
        """)

        cur.execute("""
            CREATE TABLE mental_health_condition (
                Condition_Id        INTEGER  NOT NULL,
                Disorder_Category   VARCHAR2(20),
                Episode             VARCHAR2(20),
                Treatment_Type      VARCHAR2(30),
                Risk_Factor         VARCHAR2(50),
                CONSTRAINT pk_mental_health_condition PRIMARY KEY (Condition_Id),
                CONSTRAINT fk_mh_condition_base FOREIGN KEY (Condition_Id) 
                    REFERENCES conditions(Condition_Id) ON DELETE CASCADE,
                CONSTRAINT ck_mental_episode CHECK (
                    Episode IN ('initial', 'acute', 'partial remission', 'full remission', 'multiple', 'na') 
                    OR Episode IS NULL
                )
            );
        """)

        cur.execute("""
            CREATE TABLE vitals (
                Patient_Id     INTEGER NOT NULL,
                Measure_Ts     DATE DEFAULT SYSDATE NOT NULL,
                Height_Cm      NUMBER(5,2),
                Weight_Kg      NUMBER(5,2),
                Bp_Systolic    NUMBER(3),
                Bp_Diastolic   NUMBER(3),
                Heart_Rate     NUMBER(3),
                Resp_Rate      NUMBER(3),
                Temp_C         NUMBER(4,1),
                SpO2           NUMBER(3),
                BMI            NUMBER(5,2) GENERATED ALWAYS AS (
                    CASE 
                        WHEN Height_Cm IS NOT NULL AND Height_Cm > 0 AND Weight_Kg IS NOT NULL 
                        THEN ROUND(Weight_Kg / POWER(Height_Cm/100, 2), 2)
                        ELSE NULL
                    END
                ) VIRTUAL,
                CONSTRAINT pk_vitals PRIMARY KEY (Patient_Id, Measure_Ts),
                CONSTRAINT fk_vitals_patient FOREIGN KEY (Patient_Id) REFERENCES patient(Patient_Id)
            );
                """)
        con.commit()
        con.close()
        update_text.value = "Tables created!"
        page.update()
    def drop_tables(e):
        con = sqlite3.connect("data.db")
        con.execute("DROP TABLE patient")
        con.execute("DROP TABLE doctor")
        con.execute("DROP TABLE booked")
        con.execute("DROP TABLE bill")
        con.execute("DROP TABLE medical_procedure")
        con.execute("DROP TABLE drug")
        con.execute("DROP TABLE prescription")
        con.execute("DROP TABLE diagnosis")
        con.execute("DROP TABLE conditions")
        con.execute("DROP TABLE condition_details")
        con.execute("DROP TABLE chronic_condition")
        con.execute("DROP TABLE infectious_condition")
        con.execute("DROP TABLE injury_condition")
        con.execute("DROP TABLE mental_health_condition")
        con.execute("DROP TABLE vitals")
        con.commit()
        con.close()
        update_text.value = "Tables dropped!"
        page.update()
    def populate_tables(e):
        con = sqlite3.connect("data.db")
        con.executescript("""
                          BEGIN;
                          INSERT INTO patient VALUES (100000001, 'John', 'A', 'Smith', 'M', date("1990-12-01"), '22 Bathurst St.', 'jsmith@gmail.com', '416-991-2231', 'SF12345678');
                          INSERT INTO patient VALUES (100000002, 'Amanada', NULL, 'Smith', 'F', date("1988-07-16"), '22 Bathurst St.', 'asmith@gmail.com', '416-991-2231', 'SF12345678');
                            INSERT INTO patient VALUES (100000003, 'Sandra', 'F', 'Emerson', 'F', date("2001-09-01"), '119 Sheppard Ave W', 'sandra4432@hotmail.com', '905-999-0121', NULL);
                            INSERT INTO patient VALUES (100000004, 'James', 'E', 'Emerson', 'M', date("2024-09-15"), '119 Sheppard Ave W', NULL, '905-999-0121', NULL);
                            INSERT INTO patient VALUES (100000005, 'Julian', NULL, 'Emerson', 'M', date("1999-10-02"), '119 Sheppard Ave W', 'julianemerson@gmail.com', '289-991-2646', NULL);
                            INSERT INTO patient VALUES (100000006, 'Avery', 'A', 'Jones', 'X', date("1989-03-31"), '898 Oakwood Ave.', NULL, NULL, 'GS987654321');
                          INSERT INTO doctor VALUES (100001, 'Addison', 'Montgomery', 'F', '4512', 'Gynecology', 'English', 'Active');
                            INSERT INTO doctor VALUES (100002, 'James', 'Wilson', 'M', '4513', 'Oncology', NULL, 'Active');
                            INSERT INTO doctor VALUES (100003, 'Gregory', 'House', 'M', '4514', NULL, 'Spanish', 'Inactive');
                            INSERT INTO doctor VALUES (100004, 'Robert', 'Chase', 'M', '4515', NULL, 'German', 'Active');
                            INSERT INTO doctor VALUES (100005, 'Preston', 'Burke', 'M', '4516', 'Cardiology', 'English', 'Active');
                            INSERT INTO doctor VALUES (100006, 'Meredith', 'Grey', 'F', '4517', NULL, 'English, Russian', 'Active');
                            INSERT INTO doctor VALUES (100007, 'Christina', 'Yang', 'F', '4517', 'Cardiology', 'Mandarin', 'Active');
                            INSERT INTO doctor VALUES (100008, 'Allison', 'Cameron', 'F', '4518', 'Immunology', 'English', 'Active');
                            INSERT INTO doctor VALUES (100009, 'Anita', 'Akavan', 'F', '4599', 'Psychology', 'Persian', 'Active');
                          INSERT INTO booked (Appointment_Date, Patient_Id, Doctor_Id, Appointment_Time, Reason)
                            VALUES (date("2025-10-25"), 100000001, 100001, '10:00', 'Annual check-up');
                            INSERT INTO booked (Appointment_Date, Patient_Id, Doctor_Id, Appointment_Time, Reason)
                            VALUES (date("2025-11-05"), 100000002, 100008, '14:30', 'Allergic reaction/rash');
                            INSERT INTO booked (Appointment_Date, Patient_Id, Doctor_Id, Appointment_Time, Reason)
                            VALUES (date("2025-12-10"), 100000005, 100005, '09:15', 'Cardiology follow-up');
                            INSERT INTO booked (Appointment_Date, Patient_Id, Doctor_Id, Appointment_Time, Reason)
                            VALUES (date("2025-11-16"), 100000003, 100009, '11:00', 'Initial consultation');
                            INSERT INTO bill (payer, status, amount, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES ('Insurance', 'Paid', 125.50, date("2025-10-25"), 100000001, 100001);
                            INSERT INTO bill (payer, status, amount, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES ('Patient', 'Unpaid', 75.00, date("2025-11-05"), 100000002, 100008);
                            INSERT INTO bill (payer, status, amount, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES ('Insurance', 'Unpaid', 250.75, date("2025-11-16"), 100000003, 100009);
                            INSERT INTO medical_procedure (procedure_type, location, procedure_summary, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES ('Physical', 'Exam Room 1', 'Standard physical exam with blood draw.', date("2025-10-25"), 100000001, 100001);
                            INSERT INTO medical_procedure (procedure_type, location, procedure_summary, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES ('Dermatology', 'Exam Room 3', 'Skin scraping to test for fungal infection.', date("2025-11-05"), 100000002, 100008);
                            INSERT INTO medical_procedure (procedure_type, location, procedure_summary, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES ('Consult', 'Office 2', 'Initial mental health assessment. Discussed history and treatment goals.', date(2025-11-16), 100000003, 100009);
                          INSERT INTO drug (DIN, drug_name, dosage) VALUES (1234567890, 'Amoxicillin', 500);
                            INSERT INTO drug (DIN, drug_name, dosage) VALUES (2345678901, 'Lipitor', 20);
                            INSERT INTO drug (DIN, drug_name, dosage) VALUES (3456789012, 'Zoloft', 50);
                            INSERT INTO drug (DIN, drug_name, dosage) VALUES (4567890123, 'Acetaminophen', 325);
                            INSERT INTO prescription (DIN, med_count, refills, frequency, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES (2345678901, 30, 3, 1, date("2025-10-25"), 100000001, 100001);
                            INSERT INTO prescription (DIN, med_count, refills, frequency, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES (1234567890, 14, 0, 2, date("2025-11-05"), 100000002, 100008);
                            INSERT INTO prescription (DIN, med_count, refills, frequency, Appointment_Date, Patient_Id, Doctor_Id)
                            VALUES (3456789012, 60, 1, 1, date("2025-11-16"), 100000003, 100009);
                          INSERT INTO diagnosis (Code_System, Code, Diagnosis_Name, Condition_Type)
                            VALUES ('ICD-10', 'I10', 'Essential Hypertension', 'chronic');
                            INSERT INTO diagnosis (Code_System, Code, Diagnosis_Name, Condition_Type)
                            VALUES ('ICD-10', 'J02.9', 'Acute Pharyngitis', 'infectious');
                            INSERT INTO diagnosis (Code_System, Code, Diagnosis_Name, Condition_Type)
                            VALUES ('DSM-5-TR', '300.4', 'Persistent Depressive Disorder', 'mental_health');
                            INSERT INTO diagnosis (Code_System, Code, Diagnosis_Name, Condition_Type)
                            VALUES ('ICD-10', 'S82.30', 'Fracture of Tibia', 'injury');
                            INSERT INTO conditions (Patient_Id, Diagnosis_Name, Onset_Date)
                            VALUES (100000001, 'Essential Hypertension', date("2024-05-10"));
                            INSERT INTO conditions (Patient_Id, Diagnosis_Name, Onset_Date)
                            VALUES (100000002, 'Acute Pharyngitis', date("2025-11-01"));
                            INSERT INTO conditions (Patient_Id, Diagnosis_Name, Onset_Date)
                            VALUES (100000003, 'Persistent Depressive Disorder', date("2023-01-20"));
                            INSERT INTO condition_details (Condition_Id, Patient_Id, Code_System, Code, Onset_Date, Clinical_Status, Severity, Doctor_Id)
                            VALUES (100000, 100000001, 'ICD-10', 'I10', date("2024-05-10"), 'active', 'moderate', 100001);
                            INSERT INTO condition_details (Condition_Id, Patient_Id, Code_System, Code, Onset_Date, Abatement_Date, Clinical_Status, Severity, Doctor_Id)
                            VALUES (100001, 100000002, 'ICD-10', 'J02.9', date("2025-11-01"), date("2025-11-15"), 'resolved', 'mild', 100008);
                            INSERT INTO condition_details (Condition_Id, Patient_Id, Code_System, Code, Onset_Date, Clinical_Status, Severity, Doctor_Id)
                            VALUES (100002, 100000003, 'DSM-5-TR', '300.4', date("2023-01-20"), 'active', 'moderate', 100009);
                            INSERT INTO chronic_condition (Condition_Id, Is_Lifestyle_Modifiable, Long_Term_Med_Required, Follow_Up_Interval_Months)
                            VALUES (100000, 'Y', 'Y', 6);
                            INSERT INTO infectious_condition (Condition_Id, Pathogen_Type, Isolation_Required)
                            VALUES (100001, 'virus', 'N');
                            INSERT INTO mental_health_condition (Condition_Id, Disorder_Category, Episode, Treatment_Type, Risk_Factor)
                            VALUES (100002, 'Mood Disorder', 'multiple', 'Cognitive Behavioral Therapy', 'Family History');
                            INSERT INTO vitals (Patient_Id, Measure_Ts, Height_Cm, Weight_Kg, Bp_Systolic, Bp_Diastolic, Heart_Rate, Resp_Rate, Temp_C, SpO2)
                            VALUES (100000001, date("2025-11-16"), 175.00, 80.50, 145, 95, 75, 16, 36.8, 98);
                            INSERT INTO vitals (Patient_Id, Measure_Ts, Height_Cm, Weight_Kg, Bp_Systolic, Bp_Diastolic, Heart_Rate, Resp_Rate, Temp_C, SpO2)
                            VALUES (100000002, date("2025-11-05"), 162.00, 65.00, 120, 80, 85, 18, 37.2, 97);
                            INSERT INTO vitals (Patient_Id, Measure_Ts, Height_Cm, Weight_Kg, Bp_Systolic, Bp_Diastolic, Heart_Rate, Resp_Rate, Temp_C, SpO2)
                            VALUES (100000003, date("2025-11-16"), 168.00, 58.00, 110, 70, 68, 15, 36.5, 99);
                          COMMIT;
                          """)
        con.close()
        update_text.value = "Tables populated!"
        page.update()
    def create_views(e):
        con = sqlite3.connect('data.db')
        con.executescript("""
                          BEGIN;
                            CREATE VIEW overdue_bills (Patient, Appt_Date, Amount) AS SELECT Patient_Id, Appointment_Date, Amount FROM bill
                            WHERE Status = 'Unpaid' AND ((date('now') - Appointment_Date) > 3) ORDER BY Patient_Id, Appointment_Date;

                            CREATE VIEW day_schedule_100001 (Patient, Time, Reason) AS SELECT Patient_Id, Appointment_Time, Reason FROM booked
                            WHERE Doctor_Id=100001 AND Appointment_Date=date("2025-10-25") ORDER BY Appointment_Time;

                            CREATE VIEW prescription_history (Pres_Date, Drug, DIN, Drug_Count, Dosage_Mg, Refills, Frequency, Doctor) AS
                            SELECT Appointment_Date, Drug_Name, prescription.DIN, Med_Count, Dosage, Refills, Frequency, doctor.L_Name FROM prescription, doctor, drug
                            WHERE Patient_Id=100000002
                            AND doctor.Doctor_Id = prescription.Doctor_Id
                            AND prescription.DIN = drug.DIN
                            ORDER BY Appointment_Date;
                          COMMIT;
                          """)
        con.close()
        update_text.value = "Views created!"
        page.update()
    def drop_views(e):
        con = sqlite3.connect("data.db")
        con.executescript("""
                          BEGIN;
                          DROP VIEW overdue_bills;

                          DROP VIEW day_schedule_100001;

                          DROP VIEW prescription_history;
                          COMMIT;
                          """)
        con.close()
        update_text.value = "Views dropped!"
        page.update()
    def table_queries(e):
        go_table_queries(page)
    def view_queries(e):
        go_view_queries(page)
    content = ft.SafeArea(
            ft.Column(
                [
                    ft.Text("Main Menu", size=40, weight=ft.FontWeight.BOLD),
                    update_text,
                    ft.Text("Tables", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.FilledButton(text="Create Tables", on_click=create_tables),
                            ft.FilledButton(text="Populate Tables", on_click=populate_tables),
                            ft.FilledButton(text="Drop Tables", on_click=drop_tables),
                        ]
                    ),
                    ft.Text("Views", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.FilledButton(text="Create Views", on_click=create_views),
                            ft.FilledButton(text="Drop Views", on_click=drop_views)
                        ]
                    ),
                    ft.Text("Queries", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.FilledButton(text="Table Options", on_click=table_queries),
                            ft.FilledButton(text="View Options", on_click=view_queries) 
                        ]
                    )
                ]
            )
        )
    page.controls = [content]
    page.update()

def go_table_queries(page: ft.Page):
    def back(e):
        page.window.height = 600
        page.window.width = 400
        page.controls = [content]
        page.update()
    def avg_unpaid(e):
        con = sqlite3.connect("data.db")
        res = con.execute("SELECT patient_id AS patient, AVG(amount) AS average FROM bill WHERE status='Unpaid' GROUP BY patient_id;")
        data = res.fetchall()
        con.close()
        headings = ['Patient ID', 'Average Unpaid Amount']
        page.controls = [ft.Text("Average Unpaid Bill", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def insurance(e):
        con = sqlite3.connect("data.db")
        res = con.execute("""
            SELECT patient_id, f_name, l_name, insurance
            FROM patient
            WHERE insurance IS NULL
            UNION
                SELECT patient_id, f_name, l_name, insurance
                    FROM patient
                    WHERE insurance LIKE 'SF%';
                          """)
        data = res.fetchall()
        con.close()
        headings = ['Patient ID', 'First Name', 'Last Name', 'Insurance']
        page.controls = [ft.Text("Insurance", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def no_prescriptions(e):
        con = sqlite3.connect("data.db")
        res = con.execute("""
                    SELECT patient_id AS id, f_name AS first_name, l_name AS last_name
                    FROM patient
                    WHERE patient_id IN (
                        SELECT patient_id FROM booked
                    )
                    AND patient_id NOT IN (
                        SELECT patient_id FROM prescription
                    )
                    ORDER BY patient_id;
                """)
        data = res.fetchall()
        con.close()
        headings = ['Patient ID', 'First Name', 'Last Name']
        page.controls = [ft.Text("No Prescriptions", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def num_appt(e):
        con = sqlite3.connect("data.db")
        res = con.execute("""
            SELECT DISTINCT doctor_id AS doctor, patient_id AS patient, COUNT(patient_id) AS count FROM booked GROUP BY patient_id, doctor_id ORDER BY doctor_id, patient_id;
                          """)
        data = res.fetchall()
        con.close()
        headings = ['Doctor ID', 'Patient ID', 'Count']
        page.controls = [ft.Text("Number of Appointments", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def num_doctors(e):
        con = sqlite3.connect("data.db")
        res = con.execute("""
            SELECT patient_id AS patients, COUNT(DISTINCT doctor_id) AS doctors FROM booked GROUP BY patient_id ORDER BY patient_id;
                          """)
        data = res.fetchall()
        con.close()
        headings = ['Patient ID', 'Doctor Count']
        page.controls = [ft.Text("Number of Doctors (by Patient)", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def num_patients(e):
        con = sqlite3.connect("data.db")
        res = con.execute("""
            SELECT doctor_id AS doctor, COUNT(DISTINCT patient_id) as patients FROM booked GROUP BY doctor_id ORDER BY patients DESC, doctor_id ASC;
                          """)
        data = res.fetchall()
        con.close()
        headings = ['Doctor ID', 'Patient Count']
        page.controls = [ft.Text("Number of Patients (by Doctor)", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def multi_docs(e):
        con = sqlite3.connect("data.db")
        res = con.execute("""
            SELECT DISTINCT p.patient_id AS id, f_name AS first_name, l_name AS last_name
                FROM patient p, booked b
                WHERE EXISTS
                    (SELECT b1.patient_id
                    FROM booked b1, booked b2
                    WHERE b1.doctor_id = '100002'
                    AND b1.patient_id = p.patient_id
                    AND b2.doctor_id = '100004'
                    AND b2.patient_id = b1.patient_id)
                ORDER BY p.patient_id;
                          """)
        data = res.fetchall()
        con.close()
        headings = ['Patient ID', 'First Name', 'Last Name']
        page.controls = [ft.Text("Insurance", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def make_table(headings, data):
        page.window.width = 1000
        page.window.height = 600
        columns = []
        rows = []
        for text in headings:
            columns.append(ft.DataColumn(ft.Text(text)))
        for tuple in data:
            cells = []
            for att in tuple:
                cells.append(ft.DataCell(ft.Text(att)))
            rows.append(ft.DataRow(cells=cells))
        table = ft.DataTable(columns, rows)
        page.controls.append(table)
        page.controls.append(back_button)
        page.update()
    def go_main(e):
        main_menu(page)

    content = ft.SafeArea(
            ft.Column(
                [
                    ft.Text("Table Query Menu", size=40, weight=ft.FontWeight.BOLD),
                    ft.FilledButton(text="Average unpaid bill", on_click=avg_unpaid),
                    ft.FilledButton(text="Patients with State Farm insurance or no insurance", on_click=insurance),
                    ft.FilledButton(text="Patients with no prescriptions", on_click=no_prescriptions),
                    ft.FilledButton(text="Number of appointments", on_click=num_appt),
                    ft.FilledButton(text="Number of doctors by patient", on_click=num_doctors),
                    ft.FilledButton(text="Number of patients by doctor", on_click=num_patients),
                    ft.FilledButton(text="Patients that see multiple doctors", on_click=multi_docs),
                    ft.OutlinedButton(text="Return to main menu", on_click=go_main)
                ]
            )
        )
    back_button = ft.OutlinedButton(text="Return to menu", on_click=back)
    page.controls = [content]
    page.update()

def go_view_queries(page: ft.Page):
    def back(e):
        page.window.height = 600
        page.window.width = 400
        page.controls = [content]
        page.update()
    def go_main(e):
        main_menu(page)
    def make_table(headings, data):
        page.window.width = 1000
        page.window.height = 600
        columns = []
        rows = []
        for text in headings:
            columns.append(ft.DataColumn(ft.Text(text)))
        for tuple in data:
            cells = []
            for att in tuple:
                cells.append(ft.DataCell(ft.Text(att)))
            rows.append(ft.DataRow(cells=cells))
        table = ft.DataTable(columns, rows)
        page.controls.append(table)
        page.controls.append(back_button)
        page.update()
    def prescriptions(e):
        con = sqlite3.connect("data.db")
        res = con.execute("SELECT * FROM prescription_history")
        data = res.fetchall()
        con.close()
        headings = ['Date', 'Drug', 'DIN', 'Count', 'Dosage (mg)', 'Refills', 'Frequency', 'Prescribed by ...']
        page.controls = [ft.Text("Prescription History", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def schedule(e):
        con = sqlite3.connect("data.db")
        res = con.execute("SELECT * FROM day_schedule_100001")
        data = res.fetchall()
        con.close()
        headings = ['Patient', 'Time', 'Reason']
        page.controls = [ft.Text("Doctor #100001's Schedule (Oct 25, 2025)", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)
    def unpaid(e):
        con = sqlite3.connect("data.db")
        res = con.execute("SELECT * FROM overdue_bills")
        data = res.fetchall()
        con.close()
        headings = ['Patient', 'Appointment Date', 'Amount']
        page.controls = [ft.Text("Overdue Bills", size=40, weight=ft.FontWeight.BOLD)]
        make_table(headings, data)

    content = ft.SafeArea(
            ft.Column(
                [
                    ft.Text("View Query Menu", size=40, weight=ft.FontWeight.BOLD),
                    ft.FilledButton(text="Prescription history", on_click=prescriptions),
                    ft.FilledButton(text="Doctor schedule", on_click=schedule),
                    ft.FilledButton(text="Unpaid, overdue bills", on_click=unpaid),
                    ft.OutlinedButton(text="Return to main menu", on_click=go_main)
                ]
            )
        )
    back_button = ft.OutlinedButton(text="Return to menu", on_click=back)
    page.controls = [content]
    page.update()

ft.app(main)
