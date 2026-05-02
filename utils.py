import re
class CADLParser:
    @staticmethod
    def get_dl_number(text):
        """Extracts the DL number. Supports 8 digits or 1 letter + 7 digits."""
        match = re.search(r'[A-Z]?\d{7,8}', text)

        if match:
            return match.group(0)
        return None

    @staticmethod
    def get_name(text, tag="LN"):
        """Extracts name following LN (Last Name) or FN (First Name) anchors."""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if tag in line:
                # If the tag is on its own line, the name is usually the next line
                if len(line.strip()) <= len(tag) + 1 and i + 1 < len(lines):
                    return lines[i + 1].strip()
                # Otherwise, it's on the same line
                return line.replace(tag, "").strip()
        return None

    @staticmethod
    def get_expiration_date(text):
        """Extracts the Expiration Date following the 'EXP' anchor."""
        pattern = r"EXP\s+(\d{2}/\d{2}/\d{4})"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def get_address(text):
        """Extracts the address block between FN and DOB markers."""
        pattern = r"FN\n.*?\n(.*?)\nDOB"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).replace('\n', ', ').strip()
        return None

    @staticmethod
    def get_dob(text):
        match = re.search(r'[DO0]{2}B\s*([\d\/\-]{8,12})', text, re.IGNORECASE)

        if match:
            clean = re.sub(r'[^0-9]', '', match.group(1))

            if len(clean) >= 8:
                yyyy = clean[-4:]
                remaining = clean[:-4]  # e.g., '05419'

                mm = remaining[:2]
                dd = remaining[-2:]

                # Sanity Checks
                if int(mm) > 12: mm = "0" + mm[0]
                if int(dd) > 31: dd = "0" + dd[-1]

                return f"{mm}/{dd}/{yyyy}"

        # Fallback to general date search
        dates = re.findall(r'\d{2}/\d{2}/\d{4}', text)
        return dates[1] if len(dates) >= 2 else None
