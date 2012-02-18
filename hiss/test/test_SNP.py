from hiss.protocol.snp import SNP, SNPMessage

def test_SNPSend():
    snp = SNP()
    
    msg = SNPMessage('sig')
    msg.append('register')

if __name__ == '__main__':
    test_SNPSend()
    
    