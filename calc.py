#!/usr/bin/env python3
# coding: utf-8
# Run this in Python 3.

# Author: Vaddadi Kartick
# Released under Apache license 2.0.

# This script calculates take-home pay for a given CTC, for both an employee and a consultant.
#
# Assumptions:
#  1) GST comes out of your pocket — you can't pass the GST along by grossing it up.
#  2) This is for fiscal year 2018-19.
#  3) You're a resident individual of India, not a company.
#  4) You're not a senior citizen.
#  5) Numbers are annual, and in thousands of rupees, except when stated otherwise. Take-home pay
#     is always monthly.
#  6) This script doesn't take into account the cost in your time of dealing with the bureaucratic
#     GST regime, or the cost of hiring a CA to do so.
#  7) GST paid can't be set off against something else.
#  8) HRA and LTA are ignored.
#
# Reference: https://www.bankbazaar.com/tax/income-tax-slabs.html

import sys
import math

# 25.61% of CTC goes to PF and pension. See
# https://www.bankbazaar.com/saving-schemes/guide-to-understanding-the-employee-pension-scheme.html
#
# Set this to zero if you don't want to consider this.
PF_RATE = .2561

PROFESSIONAL_TAX = 2.5

PRESUMPTIVE_RATE = .5
# Consultants benefit from presumptive taxation  at this rate. Change it if you fall under a
# different slab. Read up on presumptive taxation at https://cleartax.in/s/sugam-itr-4s-form

EMPLOYEE_TAX_DEDUCTION = 160
# Deductions you can claim if you’re an employee, but not if you're a consultant. This includes
# section 80C, 80D medical insurance, and so on. Change it as suitable.

GST_RATE = 0
# What GST rate do you fall under? Change it as suitable. If you don't pay GST at all — neither you
# nor the entity paying you is registered under GST — set this to 0. Or if you're exporting, which
# is zero-rated, set this to 0.

SLAB_1 = 250
SLAB_2 = 500
SLAB_3 = 1000

def lac(amount):
  return amount * 100

# How much income tax is due under slab 1?
def income_tax_slab_1(income):
  if income <= SLAB_1:
    return 0
  if income > SLAB_2:
    income = SLAB_2
  income -= SLAB_1
  return income * .05  # 5%

# How much income tax is due under slab 2?
def income_tax_slab_2(income):
  if income <= SLAB_2:
    return 0
  if income > SLAB_3:
    income = SLAB_3
  income -= SLAB_2
  return income * .2  # 20%

# How much income tax is due under slab 3?
def income_tax_slab_3(income):
  if income <= SLAB_3:
    return 0
  income -= SLAB_3
  return income * .3  #30%

# How much income tax is due?
def income_tax_for(income):
  if income <= 500:
    return 0
  tax = income_tax_slab_1(income) + income_tax_slab_2(income) + income_tax_slab_3(income)
  cess = tax * .04  # Health and education cess.
  surcharge = 0
  if income >= lac(100):
    print("Warning: ignoring surcharge for high income")
  if income >= lac(50):
    surcharge = tax * .1  # 10% of tax
  return tax + cess + surcharge

def income_and_professional_tax_for(income):
  return income_tax_for(income) + PROFESSIONAL_TAX

# Comprises of income tax, professional tax and GST.
def total_tax_for(income, is_employee):
  if is_employee:
    return income_and_professional_tax_for(income - EMPLOYEE_TAX_DEDUCTION) 

  EFFECTIVE_GST_RATE = GST_RATE/(1 + GST_RATE)
  # If you earn ₹100 on which you need to pay GST from your own pocket, you pay around ₹15, not ₹18.
  # Don't change this formula.

  gst = income * EFFECTIVE_GST_RATE
  income -= gst  # Income tax is net of GST.
  income *= PRESUMPTIVE_RATE
  return income_and_professional_tax_for(income) + gst

def pf_for(income):
  # To calculate PF, your salary is capped at 15K.
  return min(income, 15) * PF_RATE

def take_home(income, is_employee):
  tax = total_tax_for(income, is_employee)
  pf = pf_for(income) if is_employee else 0
  income = income - tax - pf
  return math.floor(income / 12)
  
def format_money(amount):
  if amount >= 100:
    amount /= 100
    return f"{amount} lac"
  return f"{amount}K"

def print_take_home_for(income):
  take_home_employee = format_money(take_home(income, is_employee = True))
  take_home_consultant = format_money(take_home(income, is_employee = False))
  print(f"For a CTC of {format_money(income)}, an employee takes home {take_home_employee}, while a consultant takes home {take_home_consultant}, each month.")

def print_ctc_for_take_home_pay(desired_take_home, is_employee):
  ctc = 1
  while take_home(ctc, is_employee) < desired_take_home:
    ctc += 1
  print(f"To take home {format_money(desired_take_home)} a month, you should ask for a CTC of {format_money(ctc)}")

def usage():
    print("To calculate take home from ctc:") 
    print("calc.py 12 ctc")  
    print("To calculate ctc from take home:") 
    print("calc.py 50 takehome")
          
if __name__ == '__main__':
    count = len(sys.argv[1:])
    if count <= 1 or count > 3:
        print("Invalid arguments")
        usage()
    if count == 2: 
        if sys.argv[2] == 'ctc':
            print_take_home_for(lac(float(sys.argv[1])))
        if sys.argv[2] == 'takehome':    
            print_ctc_for_take_home_pay(float(sys.argv[1]), is_employee = False)

