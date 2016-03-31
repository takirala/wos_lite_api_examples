import sys
import os.path

def main(argv):

    fileFound = False

    if len(argv) >= 1:
        print "File : " , argv[0]
        fileFound = os.path.isfile(argv[0])

    if not fileFound:
        print "Enter a valid input file"
        sys.exit(0)

    # Read the SOAP Envelope.
    # Parse the required fields.
    # Output MODS.

if __name__ == '__main__':
    main(sys.argv[1:])
