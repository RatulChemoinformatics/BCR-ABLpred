import streamlit as st
import os
import pickle
import pandas as pd
from PIL import Image
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from padelpy import padeldescriptor

# Page configuration
st.set_page_config(
  page_title='BCR-ABLpred',
  page_icon='💊',
  initial_sidebar_state='expanded')

# Session state
if 'smiles_input' not in st.session_state:
  st.session_state.smiles_input = ''

# Utilities
if os.path.isfile('molecule.smi'):
  os.remove('molecule.smi') 
  

# The App    
st.title('💊 BCR-ABLpred app')
st.info('BCR-ABLpred allow users to predict whether a query molecule is active/inactive towards the BCR-ABL target protein.')

tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs(['Main', 'About', 'What is BCR-ABL?', 'Dataset', 'Model performance', 'Python libraries', 'Citing us'])


with tab1:
  if st.session_state.smiles_input == '':
    
    with st.form('my_form'):
      st.subheader('Predict BCR-ABL inhibitory activity')

      smiles_txt = st.text_input('Enter SMILES notation', st.session_state.smiles_input)
      st.session_state.smiles_input = smiles_txt

      with st.expander('Example SMILES'):
        st.code('O=C(c1cc(Cc2n[nH]c(=O)c3ccccc23)ccc1F)N1CCN(C(=O)C2CC2)CC1')
      
      submit_button = st.form_submit_button('Submit')

      
      
      if submit_button:
        st.subheader('⚛️ Input molecule:')
        with st.expander('Show SMILES', expanded=True):
          #st.write('**SMILES**')
          st.text(st.session_state.smiles_input)

        with st.expander('Show chemical structures', expanded=True):
          #st.write('**Chemical structure**')
          smi = Chem.MolFromSmiles(st.session_state.smiles_input)
          Chem.Draw.MolToFile(smi, 'molecule.png', width=900)
          mol_image = Image.open('molecule.png')
          st.image(mol_image)

      # Input SMILES saved to file
      f = open('molecule.smi', 'w')
      f.write(f'{st.session_state.smiles_input}\tmol_001')
      f.close()


      # Compute PADEL descriptors
      if st.session_state.smiles_input != '':
        st.subheader('🔢 Descriptors')
        if os.path.isfile('molecule.smi'):
          padeldescriptor(mol_dir='molecule.smi', 
                            d_file='descriptors.csv',
                            descriptortypes='SubstructureFingerprinter.xml', 
                            detectaromaticity=True,
                            standardizenitro=True,
                            standardizetautomers=True,
                            threads=2,
                            removesalt=True,
                            log=True,
                            fingerprints=True)

        descriptors = pd.read_csv('descriptors.csv')
        descriptors.drop('Name', axis=1, inplace=True)

        with st.expander('Show full set of descriptors as calculated for query molecule'):
          #st.write('**Full set of descriptors (calculated for query molecule)**')
          st.write(descriptors)
          st.write(descriptors.shape)


      # Load descriptor subset used in trained model
      if st.session_state.smiles_input != '':
        model = pickle.load(open('model.pkl', 'rb'))
        substructure_subset = model.feature_names_in_

        query_desc_1 = descriptors.columns.difference(substructure_subset)
        query_desc_2 = descriptors.drop(query_desc_1, axis=1)

        with st.expander('Show subset of descriptors as used in trained model'):
          #st.write('**Subset of descriptors (used in trained model)**')
          st.write(query_desc_2)
          st.write(query_desc_2.shape)


      # Read in saved classification model
      if st.session_state.smiles_input != '':
        st.subheader('🤖 Predictions')
        pred = int(model.predict(query_desc_2))
        if pred == 0:
          st.error('Inactive')
        if pred == 1:
          st.success('Active')

        
with tab2:
  coverimage = Image.open('PARP1pred.jpg')
  st.image(coverimage)
with tab3:
  st.header('What is BCR-ABLpred?')
  st.write('BCR-ABL is a fusion gene that is formed as a result of the Philadelphia chromosome translocation, a chromosomal abnormality that is commonly seen in chronic myelogenous leukemia (CML). The BCR-ABL fusion gene results from a reciprocal translocation between chromosome 9 and 22, t(9;22)(q34;q11). This translocation brings together the breakpoint cluster region (BCR) gene from chromosome 22 and the Abelson (ABL) gene from chromosome 9 to form the BCR-ABL fusion gene. The protein product of this fusion gene, BCR-ABL protein, has a constitutively active tyrosine kinase that is not regulated by normal cellular control mechanisms. This leads to increased proliferation, reduced apoptosis, and altered adhesion properties of the hematopoietic cells, leading to the development of CML.')
with tab4:
  st.header('Dataset')
  st.write('''
    In our work, we retrieved a human BCR-ABL biological dataset from the ChEMBL database. The data was curated and resulted in a non-redundant set of 404 BCR-ABL inhibitors, which can be divided into:
    - 198 active compounds
    - 206 inactive compounds
    ''')
with tab5:
  st.header('Model performance')
  st.write('We selected Substructure as a molecular fingerprint and used a random forest with an oversampling approach to construct the best model. The Matthews correlation coefficients for training, cross-validation, and test sets were 1.00, 0.96, and 0.74, respectively.')
with tab6:
  st.header('Python libraries')
  st.markdown('''
    This app is based on the following Python libraries:
    - `streamlit`
    - `pandas`
    - `rdkit`
    - `padelpy`
  ''')
with tab7:
  st.markdown('Kuttappan S, Bhowmik R, Gopi Mohan C. Probing the origins of programmed death ligand-1 inhibition by implementing machine learning-assisted sequential virtual screening techniques. Molecular Diversity. 2023 Jul 20:1-8. DOI: https://doi.org/10.1007/s11030-023-10697-5.')

