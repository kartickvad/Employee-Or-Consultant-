#!/usr/bin/env python3
# coding: utf-8
# Run this in the latest version of Python. I tested with 3.7.

# Author: Kartick Vaddadi
# Released under Apache license 2.0.


# This script handles
#   - Income tax
#   - Professional tax


# This script calculates take-home pay for a given CTC, for both an employee and a consultant.
#
# Assumptions:
#  - This is for fiscal year 2019-20.
#  - You're a resident individual of India, not a company.
#  - You're not a senior citizen.
#  - Numbers are annual, and in thousands of rupees, except when stated otherwise. Take-home pay
#     is always monthly.
#  - This script doesn't take into account the cost in your time of dealing with the bureaucracy
#     regime, or the cost of hiring a CA to do so.
#  - HRA and LTA are ignored.
#  - Professional tax is calculated for Karnataka.
#
# Reference: https://www.bankbazaar.com/tax/income-tax-slabs.html

# All values are in thousands.


import math

# If your company has 10 or more employees, it's required to contribute to the
# Employees' Provident Fund (EPF), at the rate of 25.61%. Set this to zero if not applicable.
#
# See
# https://www.bankbazaar.com/saving-schemes/guide-to-understanding-the-employee-pension-scheme.html
EMPLOYEE_PF_RATE = 0.2561

# Professionals pay an extra state, which varies from state to state. In Karnataka, it's ₹200 per
# month, except for one month, where it's ₹300. This applies to both employees and consultants.
PROFESSIONAL_TAX = 2.5

# Some consultants benefit from presumptive taxation at this rate. This means that 50% of your
# income is tax-free, and only the remaining 50% is considered taxable income.
#
# But for some people, only 8% of income is considered taxable, in wihch case you should set this
# to 0.08. Others pay 6%.
#
# Read up on presumptive taxation at https://cleartax.in/s/sugam-itr-4s-form. It falls under section
# 44AD and 44ADA.
PRESUMPTIVE_RATE = .5

# Deductions you can claim if you’re an employee, but not if you're a consultant. This includes
# section 80C (up to 1.5 lakh), 80D medical insurance, and so on. Change it as suitable.
# See https://cleartax.in/s/income-tax-savings
# Instead of having separate values for each section, we've simplified our work by asking the user
# to total them up and enter the total here:
EMPLOYEE_TAX_DEDUCTION = 160

# The tax slabs are 2.5, 5 and 10 lakh:
SLAB_1 = 250
SLAB_2 = 500
SLAB_3 = 1000

def lakh(amount):
  return amount * 100

# How much income tax is due under slab 1?
def income_tax_slab_1(income):
  if income <= SLAB_1:
    return 0  # No tax under this slab, since your income is too low.
  if income > SLAB_2:
    income = SLAB_2  # Income that falls under the next slab shouldn't be taxed in this one.
  income -= SLAB_1 # Only the part of your income that exceeds the limit is taxed.
  return income * .05  # 5% tax rate for this slab

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
  # People with income less than 5 lakh pay no tax, though according to the slabs, they're required
  # to:
  if income <= 500:
    return 0
  tax = income_tax_slab_1(income) + income_tax_slab_2(income) + income_tax_slab_3(income)
  cess = tax * .04  # Health and education cess is 4% of the tax.
  surcharge = 0
  if income >= lakh(100):
    print("Warning: ignoring surcharge for high income")
  if income >= lakh(50):
    surcharge = tax * .1  # 10% of tax
  return tax + cess + surcharge

def income_and_professional_tax_for(income):
  return income_tax_for(income) + PROFESSIONAL_TAX

# Comprises of income tax and professional tax.
def total_tax_for(income, is_employee):
  if is_employee:
    return income_and_professional_tax_for(income - EMPLOYEE_TAX_DEDUCTION) 

  income *= PRESUMPTIVE_RATE
  return income_and_professional_tax_for(income)

# Calculates PF (and pension, which we don't need to worry about separately):
def pf_for(income):
  # To calculate PF, your salary is capped at 15K.
  return min(income, 15) * EMPLOYEE_PF_RATE

def take_home(income, is_employee):
  tax = total_tax_for(income, is_employee)
  pf = pf_for(income) if is_employee else 0
  income = income - tax - pf
  return math.floor(income / 12)  # Round to the nearest thousand.
  
def format_money(amount):
  if amount >= 100:
    amount /= 100
    return f"{amount} lakh"
  return f"{amount}K"

def print_take_home_for(income):
  take_home_employee = format_money(take_home(income, is_employee = True))
  take_home_consultant = format_money(take_home(income, is_employee = False))
  print(f"For a CTC of {format_money(income)}, an employee takes home {take_home_employee}, while a consultant takes home {take_home_consultant}, each month.")

def ctc_for_take_home_pay(desired_take_home, is_employee):
  ctc = 1
  while take_home(ctc, is_employee) < desired_take_home:
    ctc += 1
  return ctc

def print_ctc_for_take_home_pay(desired_take_home):
  ctc_employee = format_money(ctc_for_take_home_pay(desired_take_home, is_employee = True))
  ctc_consultant = format_money(ctc_for_take_home_pay(desired_take_home, is_employee = False))
  print(f"To take home {format_money(desired_take_home)} a month, an employee should ask for a CTC of {ctc_employee}, while a consultant should ask for a CTC of {ctc_consultant}.")
    
print_take_home_for(lakh(10))
print()
print_ctc_for_take_home_pay(50)
