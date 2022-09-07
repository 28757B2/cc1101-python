"""
Copyright (c) 2022
"""

# Valid TX powers from Design Note DN013
# fmt: off
TX_POWERS_315 = {
    0xC0:  10.6, 0xC1:  10.3, 0xC2:   9.9, 0xC3:   9.6, 0xC4:   9.2, 0xC5:   8.8, 0xC6:   8.5, 0xC7:   8.2,
    0xC8:   7.9, 0xC9:   7.5, 0xCA:   7.2, 0xCB:   6.9, 0xCC:   6.6, 0x80:   6.6, 0x81:   6.3, 0xCD:   6.3,
    0x82:   6.0, 0x83:   5.8, 0xCE:   5.6, 0x84:   5.4, 0x85:   5.0, 0x86:   4.7, 0x87:   4.3, 0x88:   3.9,
    0x89:   3.5, 0x8A:   3.1, 0xCF:   2.8, 0x8B:   2.7, 0x8C:   2.2, 0x8D:   1.7, 0x50:   0.7, 0x8E:   0.6,
    0x60:   0.5, 0x51:   0.1, 0x61:  -0.1, 0x40:  -0.3, 0x52:  -0.5, 0x62:  -0.7, 0x3F:  -0.8, 0x3E:  -1.0,
    0x53:  -1.1, 0x3D:  -1.3, 0x63:  -1.3, 0x3C:  -1.7, 0x54:  -1.7, 0x64:  -1.9, 0x3B:  -2.1, 0x55:  -2.3,
    0x65:  -2.5, 0x2F:  -2.6, 0x3A:  -2.7, 0x56:  -3.0, 0x2E:  -3.1, 0x66:  -3.1, 0x39:  -3.4, 0x57:  -3.5,
    0x2D:  -3.6, 0x67:  -3.7, 0x8F:  -4.2, 0x2C:  -4.2, 0x38:  -4.3, 0x68:  -4.3, 0x2B:  -4.9, 0x69:  -4.9,
    0x37:  -5.4, 0x6A:  -5.5, 0x2A:  -5.7, 0x6B:  -6.1, 0x29:  -6.5, 0x6C:  -6.7, 0x36:  -6.7, 0x6D:  -7.2,
    0x28:  -7.5, 0x35:  -8.1, 0x6E:  -8.4, 0x27:  -8.6, 0x26:  -9.8, 0x34:  -9.9, 0x25: -11.1, 0x33: -12.2,
    0x24: -13.0, 0x6F: -13.2, 0x1F: -13.3, 0x1E: -13.9, 0x1D: -14.5, 0x1C: -15.2, 0x23: -15.4, 0x32: -15.6,
    0x1B: -15.9, 0x1A: -16.6, 0x19: -17.5, 0x18: -18.5, 0x22: -18.8, 0x0F: -18.8, 0x0E: -19.4, 0x17: -19.6,
    0x0D: -20.0, 0x0C: -20.7, 0x16: -20.9, 0x31: -21.3, 0x0B: -21.4, 0x0A: -22.2, 0x15: -22.4, 0x09: -23.0,
    0x08: -24.0, 0x14: -24.3, 0x21: -24.5, 0x07: -25.1, 0x06: -26.4, 0x13: -26.6, 0x05: -27.7, 0x04: -29.6,
    0x12: -29.8, 0x03: -31.7, 0x02: -34.6, 0x11: -34.6, 0x01: -38.3, 0x10: -41.2, 0x30: -41.3, 0x20: -41.3,
    0x00: -63.8
}

TX_POWERS_433 = {
    0xC0:   9.9, 0xC1:   9.5, 0xC2:   9.2, 0xC3:   8.8, 0xC4:   8.5, 0xC5:   8.1, 0xC6:   7.8, 0xC7:   7.4,
    0xC8:   7.1, 0xC9:   6.8, 0xCA:   6.4, 0x80:   6.3, 0xCB:   6.1, 0x81:   6.0, 0xCC:   5.8, 0x82:   5.8,
    0xCD:   5.5, 0x83:   5.5, 0x84:   5.1, 0xCE:   4.9, 0x85:   4.8, 0x86:   4.4, 0x87:   4.0, 0x88:   3.6,
    0x89:   3.2, 0x8A:   2.8, 0x8B:   2.3, 0xCF:   2.0, 0x8C:   1.9, 0x8D:   1.4, 0x8E:   0.4, 0x50:   0.4,
    0x60:   0.1, 0x51:  -0.3, 0x61:  -0.5, 0x40:  -0.8, 0x52:  -0.9, 0x62:  -1.1, 0x3E:  -1.4, 0x53:  -1.5,
    0x63:  -1.7, 0x3C:  -2.1, 0x54:  -2.2, 0x64:  -2.3, 0x3B:  -2.5, 0x55:  -2.8, 0x65:  -2.9, 0x2F:  -3.0,
    0x3A:  -3.1, 0x56:  -3.3, 0x66:  -3.5, 0x39:  -3.8, 0x2D:  -4.0, 0x67:  -4.1, 0x8F:  -4.6, 0x68:  -4.7,
    0x69:  -5.3, 0x37:  -5.6, 0x6A:  -5.9, 0x2A:  -6.0, 0x6B:  -6.5, 0x36:  -6.8, 0x29:  -6.9, 0x6C:  -7.1,
    0x6D:  -7.7, 0x28:  -7.8, 0x35:  -8.3, 0x27:  -8.7, 0x6E:  -8.9, 0x26:  -9.9, 0x34: -10.1, 0x25: -11.4,
    0x33: -12.3, 0x24: -13.3, 0x1F: -13.7, 0x1E: -14.3, 0x1D: -14.9, 0x1C: -15.5, 0x23: -15.6, 0x32: -15.7,
    0x1B: -16.2, 0x1A: -17.0, 0x19: -17.8, 0x18: -18.8, 0x22: -19.0, 0x0F: -19.3, 0x0E: -19.8, 0x0D: -20.4,
    0x16: -21.0, 0x31: -21.3, 0x0B: -21.7, 0x0A: -22.5, 0x09: -23.3, 0x14: -24.3, 0x21: -24.5, 0x07: -25.3,
    0x13: -26.5, 0x05: -27.9, 0x04: -29.5, 0x12: -29.6, 0x03: -31.4, 0x02: -33.8, 0x01: -36.5, 0x20: -38.3,
    0x30: -38.4, 0x00: -62.7
}

TX_POWERS_868 = {
    0xC0:  10.7, 0xC1:  10.3, 0xC2:  10.0, 0xC3:   9.6, 0xC4:   9.2, 0xC5:   8.9, 0xC6:   8.5, 0xC7:   8.2,
    0xC8:   7.8, 0xC9:   7.5, 0xCA:   7.2, 0xCB:   6.8, 0xCC:   6.5, 0xCD:   6.2, 0xCE:   5.5, 0x80:   5.2,
    0x81:   5.0, 0x82:   4.8, 0x83:   4.6, 0x84:   4.4, 0x85:   4.1, 0x86:   3.7, 0x87:   3.4, 0x88:   3.0,
    0x89:   2.6, 0xCF:   2.4, 0x8A:   2.1, 0x8B:   1.7, 0x8C:   1.1, 0x8D:   0.6, 0x50:  -0.3, 0x60:  -0.5,
    0x8E:  -0.5, 0x51:  -0.9, 0x61:  -1.1, 0x40:  -1.5, 0x52:  -1.6, 0x62:  -1.8, 0x53:  -2.3, 0x63:  -2.4,
    0x3F:  -2.6, 0x3E:  -2.8, 0x54:  -2.9, 0x64:  -3.1, 0x3D:  -3.2, 0x3C:  -3.5, 0x55:  -3.6, 0x65:  -3.7,
    0x3B:  -4.0, 0x56:  -4.2, 0x66:  -4.4, 0x2F:  -4.5, 0x3A:  -4.5, 0x57:  -4.8, 0x2E:  -4.9, 0x67:  -5.0,
    0x39:  -5.2, 0x2D:  -5.5, 0x68:  -5.7, 0x8F:  -6.0, 0x2C:  -6.0, 0x38:  -6.1, 0x69:  -6.3, 0x2B:  -6.7,
    0x6A:  -6.9, 0x37:  -6.9, 0x2A:  -7.4, 0x6B:  -7.5, 0x36:  -8.1, 0x29:  -8.2, 0x6C:  -8.7, 0x28:  -9.0,
    0x35:  -9.4, 0x27:  -9.8, 0x26: -11.0, 0x34: -11.1, 0x25: -12.5, 0x33: -13.3, 0x24: -14.3, 0x6D: -14.5,
    0x1F: -14.6, 0x1E: -15.1, 0x1D: -15.7, 0x1C: -16.4, 0x23: -16.5, 0x32: -16.5, 0x1B: -17.0, 0x1A: -17.8,
    0x19: -18.6, 0x18: -19.5, 0x22: -19.6, 0x0F: -20.0, 0x0E: -20.5, 0x17: -20.5, 0x0D: -21.1, 0x0C: -21.7,
    0x16: -21.7, 0x31: -21.9, 0x0B: -22.3, 0x0A: -23.0, 0x15: -23.0, 0x09: -23.8, 0x08: -24.6, 0x14: -24.7,
    0x21: -24.8, 0x07: -25.5, 0x13: -26.5, 0x06: -26.5, 0x05: -27.7, 0x12: -28.9, 0x04: -28.9, 0x03: -30.2,
    0x02: -31.7, 0x11: -31.7, 0x01: -33.1, 0x10: -34.1, 0x20: -34.1, 0x30: -34.2, 0x6E: -45.8, 0x00: -59.3,
    0x6F: -69.2
}

TX_POWERS_915 = {
    0xC0:   9.4, 0xC1:   9.0, 0xC2:   8.6, 0xC3:   8.3, 0xC4:   7.9, 0xC5:   7.6, 0xC6:   7.2, 0xC7:   6.9,
    0xC8:   6.6, 0xC9:   6.2, 0xCA:   5.9, 0xCB:   5.6, 0xCC:   5.3, 0xCD:   5.0, 0x80:   4.9, 0x81:   4.7,
    0x82:   4.5, 0xCE:   4.3, 0x83:   4.2, 0x84:   3.9, 0x85:   3.6, 0x86:   3.3, 0x87:   2.9, 0x88:   2.5,
    0x89:   2.2, 0x8A:   1.8, 0xCF:   1.6, 0x8B:   1.3, 0x8C:   0.9, 0x8D:   0.5, 0x8E:  -0.6, 0x50:  -0.9,
    0x60:  -1.1, 0x51:  -1.6, 0x61:  -1.8, 0x40:  -2.1, 0x52:  -2.2, 0x62:  -2.4, 0x3F:  -2.5, 0x3E:  -2.7,
    0x53:  -2.9, 0x3D:  -3.0, 0x63:  -3.0, 0x3C:  -3.4, 0x22: -19.4, 0x0F: -19.7, 0x0E: -20.2, 0x17: -20.3,
    0x0D: -20.8, 0x0C: -21.4, 0x16: -21.4, 0x31: -21.7, 0x0B: -22.0, 0x0A: -22.7, 0x15: -22.8, 0x09: -23.5,
    0x6D: -23.8, 0x08: -24.3, 0x14: -24.4, 0x21: -24.6, 0x07: -25.2, 0x13: -26.2, 0x06: -26.2, 0x05: -27.3,
    0x12: -28.6, 0x04: -28.6, 0x03: -29.8, 0x02: -31.2, 0x11: -31.3, 0x01: -32.7, 0x10: -33.6, 0x20: -33.7,
    0x30: -33.7, 0x00: -58.2, 0x6E: -64.5, 0x6F: -69.7
}
# fmt: on