import pandas as pd
import os
from pipeline import enrich_acitivites, clean, enrich_materials, conformance_checking

def main():
    enrich_acitivites.run()
    clean.run()
    enrich_materials.run()
    conformance_checking.run()

    print("Conformance Checking done!")

if __name__ == "__main__":
    main()
