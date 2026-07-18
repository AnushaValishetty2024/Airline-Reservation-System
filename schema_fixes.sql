-- Add gender and date_of_birth columns to passengers table
ALTER TABLE passengers 
ADD COLUMN IF NOT EXISTS gender VARCHAR(20) DEFAULT NULL AFTER passport_number,
ADD COLUMN IF NOT EXISTS date_of_birth DATE DEFAULT NULL AFTER gender;

-- Update existing passengers with sample data
UPDATE passengers SET gender = 'Male', date_of_birth = '1985-03-15' WHERE id = 1;
UPDATE passengers SET gender = 'Female', date_of_birth = '1990-07-22' WHERE id = 2;