for F in *.jpeg; do sips -s format jpeg $F --out ${F/.jpeg/.jpg}; done
for F in *.JPG; do sips -s format jpeg $F --out ${F/.JPG/.jpg}; done
for F in *.png; do sips -s format jpeg $F --out ${F/.png/.jpg}; done
for F in *.gif; do sips -s format jpeg $F --out ${F/.gif/.jpg}; done

