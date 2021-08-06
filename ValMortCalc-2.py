import sys
import getopt
import subprocess
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionPatch
from prettytable import PrettyTable


def usage():
    print ("Val's Mortgage Calculator Tool")
    print ("")
    print ("")
    print ("Usage: mortCalc.py -n name_of_person -c mortgage_conf -a mortgage_amnt -d down_payment -i interest_rate -t mortgage_duration -m add_monthly, -y add_yearly")
    print ("")
    print ("Options: -n, -c, -a, -d, -i, -t, -m, -y")
    print ("")
    print ("-n --name_of_person	- User of the app is required to enter his or her name")
    print ("-c --mortgage_conf	- Mortgage configuration type is selected as either yes with down payment or no without down payment")
    print ("-a --mortgage_amnt	- User enter the amount of money taken for mortgage")
    print ("-d --down_payment	- User enter the amount of money that he/she will pay upfront when taking the loan")
    print ("-i --interest_rate	- User sets the interest rate on the loan as a fixed interest rate as a percentage")
    print ("-t --mortgage_duration	- User specifies the amount of time he or she will take to repay the mortgage loan in years")
    print ("-m --add_monthly	- User enter any additional monthly payments that he/she will be making towards the loan")
    print ("-y --add_yearly	- User enter any additional yearly payments that he/she will be making towards the loan")
    print ("")
    print ("")
    print ("Examples: ")
    print ("mortCalc.py -n ValAudi -c yes -a 230000 -d 115000 -i 2.607 -t 15 -m 0 -y 0")
    print ("mortCalc.py -n ValAudi -c no -a 230000 -d 0 -i 2.607 -t 15 -m 0 -y -y 0")
    
    sys.exit(0)

def main():
    global name_of_person
    global mortgage_conf 
    global mortgage_amnt
    global down_payment
    global interest_rate
    global mortgage_duration
    global add_monthly
    global add_yearly


    if not len(sys.argv[1:]):
        usage()
        
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hn:c:a:d:i:t:m:y:", ["help","name_of_person","mortgage_conf","mortgage_amnt","down_payment","interest_rate","mortgage_duration","add_monthly","add_yearly"])
    except getopt.GetoptError as err:
        print (err)
        opts = []
        usage()
            
            
    for opt,arg in opts:
        if opt in ["-h", "--help"]:
            usage()
        elif opt in ["-n", "--name_of_person"]:
            name_of_person = arg
        elif opt in ["-c", "--mortgage_conf "]:
            mortgage_conf = arg
        elif opt in ["-a", "--mortgage_amnt"]:
            mortgage_amnt = float(arg)
        elif opt in ["-d", "--down_payment"]:
            down_payment = float(arg)
        elif opt in ["-i", "--interest_rate"]:
            interest_rate = float(arg)
        elif opt in ["-t", "--mortgage_duration"]:
            mortgage_duration = int(arg)
        elif opt in ["-m", "--add_monthly"]:
            add_monthly = float(arg)
        elif opt in ["-y", "--add_yearly"]:
            add_yearly = float(arg)
        else:
            assert False, "Unhandled Option"

# Calculate total interest on loan and the total amount payable back.
    totalInterest = (mortgage_amnt - down_payment)*(interest_rate/100)
    totalAmountPayable = (mortgage_amnt - down_payment) + totalInterest
    
# Compute duration for repayment in case of additional monthly and yearly payments and show savings
    Duration = yearlyPayments(mortgage_amnt, down_payment, interest_rate, mortgage_duration, add_monthly, add_yearly)
    interestSavings = savings(Duration)
    
# Obtain monthly details for the population of the amortization table and generate the amortization table
    MonthlyDetails = monthlyPayments(down_payment)
    breakdown = TableData(MonthlyDetails)
            
# Create an Output file for the Mortgage configuration
    OveralFile = open("Amortization.txt", "a+")
    OveralFile.write("For the following Mortgage configurations\n")
    OveralFile.write ("\n")
    OveralFile.write("Down payment: %f\r\n" % (down_payment))
    OveralFile.write("Interest rate: %f\r\n" % (interest_rate))
    OveralFile.write("Mortgage Duration: %d\r\n" % (mortgage_duration))
    OveralFile.write("Additional monthly payments: %f\r\n" % (add_monthly))
    OveralFile.write("Additional yearly payments: %f\r\n" % (add_yearly))
    OveralFile.write("\n")
    OveralFile.write("\n")
    OveralFile.write("The total Interest paid will be: %f\r\n" % (totalInterest - interestSavings))
    OveralFile.write("The total Amount paid back will be: %f\r\n" % (mortgage_amnt + totalInterest))
    OveralFile.write("\n")
    OveralFile.write("************************************************************************************************************************\n")
    OveralFile.write("\n")
    OveralFile.write('{0}\n' .format(breakdown))
    OveralFile.write("\n")
    OveralFile.close()
    
# Create a visual representation of the savings made
    fig = plt.figure(figsize = (9, 5.0625))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    fig.subplots_adjust(wspace=0)
    
    
    ratios = [(totalInterest/totalAmountPayable), ((mortgage_amnt - down_payment)/totalAmountPayable)]
    labels = ['INTEREST','PRINCIPAL']
    explode = [0.1, 0]
    angle = -180 * ratios[0]
    ax1.pie(ratios, autopct='%1.1f%%', startangle=angle, labels=labels, explode=explode)
    xpos = 0
    bottom = 0
    ratios = [(interestSavings/totalInterest), ((totalInterest - interestSavings)/totalInterest)]
    width = .2
    colors = [[.1, .3, .5], [.1, .3, .3], [.1, .3, .7], [.1, .3, .9]]
    
    for j in range(len(ratios)):
        height = ratios[j]
        ax2.bar(xpos, height, width, bottom=bottom, color=colors[j])
        ypos = bottom + ax2.patches[j].get_height() / 2
        bottom += height
        ax2.text(xpos, ypos, "%d%%" % (ax2.patches[j].get_height() * 100), ha='center')

    ax2.set_title('Interest Breakdown')
    ax2.legend(('Interest to be Paid', 'Potential Savings'))
    ax2.axis('off')
    ax2.set_xlim(- 2.5 * width, 2.5 * width)

    # use ConnectionPatch to draw lines between the two plots
    # get the wedge data
    theta1, theta2 = ax1.patches[0].theta1, ax1.patches[0].theta2
    center, r = ax1.patches[0].center, ax1.patches[0].r
    bar_height = sum([item.get_height() for item in ax2.patches])

    # draw top connecting line
    x = r * np.cos(np.pi / 180 * theta2) + center[0]
    y = np.sin(np.pi / 180 * theta2) + center[1]
    con = ConnectionPatch(xyA=(- width / 2, bar_height), xyB=(x, y), coordsA="data", coordsB="data", axesA=ax2, axesB=ax1)
    con.set_color([0, 0, 0])
    con.set_linewidth(4)
    ax2.add_artist(con)

    # draw bottom connecting line
    x = r * np.cos(np.pi / 180 * theta1) + center[0]
    y = np.sin(np.pi / 180 * theta1) + center[1]
    con = ConnectionPatch(xyA=(- width / 2, 0), xyB=(x, y), coordsA="data", coordsB="data", axesA=ax2, axesB=ax1)
    con.set_color([0, 0, 0])
    ax2.add_artist(con)
    con.set_linewidth(4)

    plt.show()
# End of code


def monthlyPayments(down_payment):
    monthlyPrincipal = (mortgage_amnt - down_payment)/(mortgage_duration*12)
    monthlyInterest = ((mortgage_amnt - down_payment) *(interest_rate/100))/12
    monthlyPayment = monthlyPrincipal + monthlyInterest + add_monthly
    return [monthlyPrincipal, monthlyInterest, monthlyPayment]

# def savings(down_payment):
#    timeSaved = mortgage_duration*12 - (mortgage_amnt/(monthlyPrincipal + add_monthly))
#    SavingsOnInterest = timeSaved * monthlyInterest

def yearlyPayments(mortgage_amnt, down_payment, interest_rate, mortgage_duration, add_monthly, add_yearly):
    yearlyPrincipal = (((mortgage_amnt - down_payment/(mortgage_duration*12)) + add_monthly) * 12) + add_yearly
    timeSaved = (mortgage_duration*12) - (((mortgage_amnt - down_payment)/(yearlyPrincipal)) * 12)
    return timeSaved
    
def savings(timeSaved):
    SavingsOnInterest = timeSaved * (((mortgage_amnt - down_payment)*(interest_rate/100))/12)
    return SavingsOnInterest

def TableData(MonthlyDetails):
    monthlyPrincipal = MonthlyDetails[0]
    monthlyInterest = MonthlyDetails[1]
    monthlyPayments = MonthlyDetails[2]
    amortTable = PrettyTable()
    amortTable.field_names = ["Month", "Monthly Principal", "Monthly Interest", "Total Monthly Payment", "Current Balance"]
    month = 0
    currentValue = [mortgage_amnt - down_payment]
    while currentValue[0] > monthlyPayments:
        month += 1
        currentValue = [currentValue[0] - MonthlyDetails[2]]
        amortTable.add_row([month] + MonthlyDetails + currentValue)
    if currentValue[0] < monthlyPrincipal:
        month += 1
        if currentValue[0] < monthlyInterest:
            MonthlyDetails = [0, currentValue, currentValue]
            amortTable.add_row([month] + MonthlyDetails + currentValue)
        MonthlyDetails = [monthlyPrincipal, (currentValue - monthlyPrincipal), currentValue]
        amortTable.add_row([month] + MonthlyDetails + currentValue)
    return amortTable

main()

