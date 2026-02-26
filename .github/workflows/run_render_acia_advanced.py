"""
ACIA for Render Cloud Platform - Advanced Real Data Extraction
LinkedIn, Greenhouse-Stripe, Internshala, WeWorkRemotely, SimplyHired, Naukri
Advanced scraping with multiple extraction methods and fallbacks
"""

import os
import sys
import logging
import time
from datetime import datetime
import requests
import re
import json
from bs4 import BeautifulSoup

def setup_logging():
    """Setup logging for Render"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('acia_render_advanced.log', mode='a'),
            logging.StreamHandler()
        ]
    )

def fetch_stripe_internships():
    """Fetch internships from Stripe Greenhouse (Real API)"""
    try:
        print("🔍 Fetching Stripe internships...")
        internships = []
        
        url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        jobs = response.json().get('jobs', [])
        
        for job in jobs:
            try:
                title = job.get('title', '').lower()
                if 'intern' in title:
                    location_info = job.get('location', {})
                    location = location_info.get('name', 'Not specified')
                    
                    internship = {
                        'company': 'Stripe',
                        'role': job.get('title', 'Unknown Role'),
                        'location': location,
                        'link': job.get('absolute_url', ''),
                        'source': 'Greenhouse-Stripe',
                        'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    internships.append(internship)
                    print(f"  📋 {internship['role']} at {internship['company']}")
            except Exception as e:
                print(f"    ⚠️  Error processing job: {e}")
                continue
        
        print(f"✅ Fetched {len(internships)} Stripe internships")
        return internships
        
    except Exception as e:
        print(f"❌ Stripe request failed: {e}")
        return []

def fetch_linkedin_internships():
    """Fetch internships from LinkedIn (Advanced Extraction)"""
    try:
        print("🔍 Fetching LinkedIn internships...")
        internships = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Method 1: Try API
        try:
            search_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            params = {
                'keywords': 'data science intern machine learning ai python software engineering',
                'location': 'India',
                'f_TPR': 'r86400',
                'start': 0
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'elements' in data:
                        for element in data.get('elements', [])[:10]:
                            try:
                                job = element.get('job', {})
                                title = job.get('title', 'Unknown Role')
                                
                                if 'intern' in title.lower():
                                    company = job.get('companyName', 'Unknown Company')
                                    location = job.get('formattedLocation', 'Not specified')
                                    job_id = job.get('id', '')
                                    
                                    internship = {
                                        'company': company,
                                        'role': title,
                                        'location': location,
                                        'link': f"https://www.linkedin.com/jobs/view/{job_id}",
                                        'source': 'LinkedIn',
                                        'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }
                                    internships.append(internship)
                                    print(f"  📋 {internship['role']} at {internship['company']}")
                            except Exception as e:
                                print(f"    ⚠️  Error processing LinkedIn job: {e}")
                                continue
                except:
                    pass
        except:
            pass
        
        # Method 2: Try web scraping
        if len(internships) == 0:
            try:
                web_url = "https://www.linkedin.com/jobs/search?keywords=data%20science%20intern&location=India&f_TPR=r86400"
                response = requests.get(web_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for job cards
                    job_cards = soup.find_all('div', class_='base-card') or soup.find_all('li', class_='job-result-card')
                    
                    for card in job_cards[:8]:
                        try:
                            # Extract title
                            title_element = card.find('h3') or card.find('a', class_='base-card__full-link')
                            title = title_element.get_text().strip() if title_element else 'Unknown Role'
                            
                            if 'intern' in title.lower():
                                # Extract company
                                company_element = card.find('h4') or card.find('span', class_='hidden-nested-link')
                                company = company_element.get_text().strip() if company_element else 'Unknown Company'
                                
                                # Extract location
                                location_element = card.find('span', class_='job-result-card__location') or card.find('span', class_='job-search-card__location')
                                location = location_element.get_text().strip() if location_element else 'India'
                                
                                # Extract link
                                link_element = card.find('a', href=True)
                                if link_element:
                                    href = link_element.get('href', '')
                                    if href.startswith('/'):
                                        link = 'https://www.linkedin.com' + href
                                    elif 'linkedin.com' in href:
                                        link = href
                                    else:
                                        continue
                                else:
                                    continue
                                
                                internship = {
                                    'company': company,
                                    'role': title,
                                    'location': location,
                                    'link': link,
                                    'source': 'LinkedIn',
                                    'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                internships.append(internship)
                                print(f"  📋 {internship['role']} at {internship['company']}")
                        except Exception as e:
                            print(f"    ⚠️  Error processing LinkedIn card: {e}")
                            continue
            except:
                pass
        
        # Method 3: Try alternative search
        if len(internships) == 0:
            try:
                alt_url = "https://www.linkedin.com/jobs/search?keywords=internship%20data%20science&location=India"
                response = requests.get(alt_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for any job listings
                    job_elements = soup.find_all(['h3', 'h2', 'a'], text=re.compile(r'(?i)intern', re.IGNORECASE))
                    
                    for element in job_elements[:5]:
                        try:
                            if element.name == 'a':
                                title = element.get_text().strip()
                                href = element.get('href', '')
                                if 'linkedin.com' in href:
                                    link = href
                                else:
                                    continue
                            else:
                                # Look for nearby link
                                link_element = element.find('a') or element.parent.find('a') if element.parent else None
                                if link_element:
                                    title = element.get_text().strip()
                                    href = link_element.get('href', '')
                                    if 'linkedin.com' in href:
                                        link = href
                                    else:
                                        continue
                                else:
                                    continue
                            
                            if 'intern' in title.lower():
                                # Extract company from title or nearby text
                                company_match = re.search(r'at\s+([^\n]+)', title, re.IGNORECASE)
                                company = company_match.group(1).strip() if company_match else 'Tech Company'
                                
                                internship = {
                                    'company': company,
                                    'role': title,
                                    'location': 'India',
                                    'link': link,
                                    'source': 'LinkedIn',
                                    'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                internships.append(internship)
                                print(f"  📋 {internship['role']} at {internship['company']}")
                        except Exception as e:
                            print(f"    ⚠️  Error processing LinkedIn element: {e}")
                            continue
            except:
                pass
        
        print(f"✅ Fetched {len(internships)} LinkedIn internships")
        return internships
        
    except Exception as e:
        print(f"❌ LinkedIn fetch error: {e}")
        return []

def fetch_internshala_internships():
    """Fetch internships from Internshala (Advanced Extraction)"""
    try:
        print("🔍 Fetching Internshala internships...")
        internships = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Method 1: Try main search page
        urls_to_try = [
            "https://internshala.com/internships/data-science-internship-in-india",
            "https://internshala.com/internships/data-science-internship",
            "https://internshala.com/internships/search?keywords=data%20science",
            "https://internshala.com/internships"
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=20)
                response.raise_for_status()
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try different selectors
                    selectors_to_try = [
                        'div.internship_meta',
                        'div.individual_internship',
                        'article.internship-card',
                        'div.job-container',
                        'div.internship-card',
                        'li.internship',
                        'div[class*="internship"]',
                        'a[href*="internship"]'
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            if '[' in selector:
                                # CSS selector
                                internship_cards = soup.select(selector)
                            else:
                                # Class selector
                                internship_cards = soup.find_all('div', class_=selector) or soup.find_all('article', class_=selector) or soup.find_all('li', class_=selector)
                            
                            if internship_cards:
                                for card in internship_cards[:10]:
                                    try:
                                        # Extract title
                                        title_element = card.find('a') or card.find('h3') or card.find('h4') or card.find('span', class_='title')
                                        title = title_element.get_text().strip() if title_element else 'Unknown Role'
                                        
                                        # Extract company
                                        company_element = card.find('span', class_='company') or card.find('div', class_='company') or card.find('a', class_='company-name')
                                        company = company_element.get_text().strip() if company_element else 'Unknown Company'
                                        
                                        # Extract location
                                        location_element = card.find('span', class_='location') or card.find('div', class_='location') or card.find('a', class_='location-link')
                                        location = location_element.get_text().strip() if location_element else 'Not specified'
                                        
                                        # Extract link
                                        link_element = card.find('a', href=True)
                                        if link_element:
                                            href = link_element.get('href', '')
                                            if href.startswith('/'):
                                                link = 'https://internshala.com' + '/' + href
                                            elif href.startswith('http'):
                                                link = href
                                            else:
                                                link = 'https://internshala.com' + '/' + href
                                        else:
                                            continue
                                        
                                        if ('intern' in title.lower() or 'internship' in title.lower()) and company != 'Unknown Company':
                                            internship = {
                                                'company': company,
                                                'role': title,
                                                'location': location,
                                                'link': link,
                                                'source': 'Internshala',
                                                'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            }
                                            internships.append(internship)
                                            print(f"  📋 {internship['role']} at {internship['company']}")
                                    except Exception as e:
                                        print(f"    ⚠️  Error processing Internshala card: {e}")
                                        continue
                                
                                if len(internships) > 0:
                                    break
                        except:
                            continue
                            
                    if len(internships) > 0:
                        break
                        
            except:
                continue
        
        # Method 2: Try to find any internship links
        if len(internships) == 0:
            try:
                response = requests.get("https://internshala.com", headers=headers, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for any links containing 'internship'
                    links = soup.find_all('a', href=re.compile(r'internship', re.IGNORECASE))
                    
                    for link in links[:5]:
                        try:
                            title = link.get_text().strip()
                            href = link.get('href', '')
                            
                            if 'internship' in title.lower() and href:
                                if href.startswith('/'):
                                    full_link = 'https://internshala.com' + href
                                elif href.startswith('http'):
                                    full_link = href
                                else:
                                    continue
                                
                                # Extract company from title
                                company_match = re.search(r'at\s+([^\n|]+)', title, re.IGNORECASE)
                                company = company_match.group(1).strip() if company_match else 'Company'
                                
                                internship = {
                                    'company': company,
                                    'role': title,
                                    'location': 'India',
                                    'link': full_link,
                                    'source': 'Internshala',
                                    'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                internships.append(internship)
                                print(f"  📋 {internship['role']} at {internship['company']}")
                        except Exception as e:
                            print(f"    ⚠️  Error processing Internshala link: {e}")
                            continue
            except:
                pass
        
        print(f"✅ Fetched {len(internships)} Internshala internships")
        return internships
        
    except Exception as e:
        print(f"❌ Internshala request failed: {e}")
        return []

def fetch_weworkremotely_internships():
    """Fetch internships from WeWorkRemotely (Advanced Extraction)"""
    try:
        print("🔍 Fetching WeWorkRemotely internships...")
        internships = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Method 1: Try main search
        urls_to_try = [
            "https://weworkremotely.com/remote-jobs/search?term=intern",
            "https://weworkremotely.com/remote-jobs/search?term=internship",
            "https://weworkremotely.com/remote-jobs/search?term=data%20science%20intern",
            "https://weworkremotely.com/remote-jobs/search?term=python%20intern"
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try different selectors
                    selectors_to_try = [
                        'li.feature',
                        'article.job',
                        'div.job-listing',
                        'div[class*="job"]',
                        'li[class*="feature"]',
                        'a[title*="Intern"]'
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            if '[' in selector:
                                job_listings = soup.select(selector)
                            else:
                                job_listings = soup.find_all('li', class_=selector) or soup.find_all('article', class_=selector) or soup.find_all('div', class_=selector)
                            
                            if job_listings:
                                for listing in job_listings[:10]:
                                    try:
                                        # Extract title and link
                                        title_link = listing.find('a', class_='title') or listing.find('h2') or listing.find('a')
                                        if title_link:
                                            title = title_link.get_text().strip()
                                            href = title_link.get('href', '')
                                            if href.startswith('/'):
                                                link = 'https://weworkremotely.com' + href
                                            elif href.startswith('http'):
                                                link = href
                                            else:
                                                continue
                                        else:
                                            continue
                                        
                                        # Extract company
                                        company_element = listing.find('span', class_='company') or listing.find('div', class_='company') or listing.find('span', class_='name')
                                        company = company_element.get_text().strip() if company_element else 'Unknown Company'
                                        
                                        # Extract location
                                        location_element = listing.find('span', class_='location') or listing.find('div', class_='location')
                                        location = location_element.get_text().strip() if location_element else 'Remote'
                                        
                                        if 'intern' in title.lower() and company != 'Unknown Company':
                                            internship = {
                                                'company': company,
                                                'role': title,
                                                'location': location,
                                                'link': link,
                                                'source': 'WeWorkRemotely',
                                                'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            }
                                            internships.append(internship)
                                            print(f"  📋 {internship['role']} at {internship['company']}")
                                    except Exception as e:
                                        print(f"    ⚠️  Error processing WeWorkRemotely listing: {e}")
                                        continue
                                
                                if len(internships) > 0:
                                    break
                        except:
                            continue
                            
                    if len(internships) > 0:
                        break
                        
            except:
                continue
        
        # Method 2: Try to find any internship mentions
        if len(internships) == 0:
            try:
                response = requests.get("https://weworkremotely.com", headers=headers, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for any text containing 'intern'
                    elements = soup.find_all(text=re.compile(r'intern', re.IGNORECASE))
                    
                    for element in elements[:5]:
                        try:
                            parent = element.parent
                            if parent and parent.name == 'a':
                                title = parent.get_text().strip()
                                href = parent.get('href', '')
                                
                                if 'intern' in title.lower() and href:
                                    if href.startswith('/'):
                                        link = 'https://weworkremotely.com' + href
                                    elif href.startswith('http'):
                                        link = href
                                    else:
                                        continue
                                    
                                    # Extract company
                                    company_match = re.search(r'at\s+([^\n|]+)', title, re.IGNORECASE)
                                    company = company_match.group(1).strip() if company_match else 'Remote Company'
                                    
                                    internship = {
                                        'company': company,
                                        'role': title,
                                        'location': 'Remote',
                                        'link': link,
                                        'source': 'WeWorkRemotely',
                                        'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }
                                    internships.append(internship)
                                    print(f"  📋 {internship['role']} at {internship['company']}")
                        except Exception as e:
                            print(f"    ⚠️  Error processing WeWorkRemotely element: {e}")
                            continue
            except:
                pass
        
        print(f"✅ Fetched {len(internships)} WeWorkRemotely internships")
        return internships
        
    except Exception as e:
        print(f"❌ WeWorkRemotely request failed: {e}")
        return []

def fetch_simplyhired_internships():
    """Fetch internships from SimplyHired (Advanced Extraction)"""
    try:
        print("🔍 Fetching SimplyHired internships...")
        internships = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Method 1: Try main search
        urls_to_try = [
            "https://www.simplyhired.co.in/internship-jobs/data-science-in-india",
            "https://www.simplyhired.co.in/internship-jobs/data-science",
            "https://www.simplyhired.co.in/job-search?q=data+science+intern",
            "https://www.simplyhired.co.in/jobs?q=internship+data+science"
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try different selectors
                    selectors_to_try = [
                        'div.jobposting',
                        'article.job',
                        'div.job-listing',
                        'div[class*="job"]',
                        'li.jobposting',
                        'div.SerpJob',
                        'a[href*="job"]'
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            if '[' in selector:
                                job_cards = soup.select(selector)
                            else:
                                job_cards = soup.find_all('div', class_=selector) or soup.find_all('article', class_=selector) or soup.find_all('li', class_=selector)
                            
                            if job_cards:
                                for card in job_cards[:10]:
                                    try:
                                        # Extract title
                                        title_element = card.find('h2') or card.find('h3') or card.find('a', class_='title') or card.find('span', class_='job-title')
                                        title = title_element.get_text().strip() if title_element else 'Unknown Role'
                                        
                                        # Extract company
                                        company_element = card.find('span', class_='company') or card.find('div', class_='company') or card.find('span', class_='jobposting-company')
                                        company = company_element.get_text().strip() if company_element else 'Unknown Company'
                                        
                                        # Extract location
                                        location_element = card.find('span', class_='location') or card.find('div', class_='location') or card.find('span', class_='jobposting-location')
                                        location = location_element.get_text().strip() if location_element else 'Not specified'
                                        
                                        # Extract link
                                        link_element = card.find('a', class_='jobposting-title') or card.find('a', href=True)
                                        if link_element:
                                            href = link_element.get('href', '')
                                            if href.startswith('http'):
                                                link = href
                                            elif href.startswith('/'):
                                                link = 'https://www.simplyhired.co.in' + href
                                            else:
                                                continue
                                        else:
                                            continue
                                        
                                        if ('intern' in title.lower() or 'internship' in title.lower()) and company != 'Unknown Company':
                                            internship = {
                                                'company': company,
                                                'role': title,
                                                'location': location,
                                                'link': link,
                                                'source': 'SimplyHired',
                                                'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            }
                                            internships.append(internship)
                                            print(f"  📋 {internship['role']} at {internship['company']}")
                                    except Exception as e:
                                        print(f"    ⚠️  Error processing SimplyHired card: {e}")
                                        continue
                                
                                if len(internships) > 0:
                                    break
                        except:
                            continue
                            
                    if len(internships) > 0:
                        break
                        
            except:
                continue
        
        # Method 2: Try to find any internship mentions
        if len(internships) == 0:
            try:
                response = requests.get("https://www.simplyhired.co.in", headers=headers, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for any text containing 'intern'
                    elements = soup.find_all(text=re.compile(r'intern', re.IGNORECASE))
                    
                    for element in elements[:5]:
                        try:
                            parent = element.parent
                            if parent and parent.name == 'a':
                                title = parent.get_text().strip()
                                href = parent.get('href', '')
                                
                                if 'intern' in title.lower() and href:
                                    if href.startswith('http'):
                                        link = href
                                    elif href.startswith('/'):
                                        link = 'https://www.simplyhired.co.in' + href
                                    else:
                                        continue
                                    
                                    # Extract company
                                    company_match = re.search(r'at\s+([^\n|]+)', title, re.IGNORECASE)
                                    company = company_match.group(1).strip() if company_match else 'Indian Company'
                                    
                                    internship = {
                                        'company': company,
                                        'role': title,
                                        'location': 'India',
                                        'link': link,
                                        'source': 'SimplyHired',
                                        'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }
                                    internships.append(internship)
                                    print(f"  📋 {internship['role']} at {internship['company']}")
                        except Exception as e:
                            print(f"    ⚠️  Error processing SimplyHired element: {e}")
                            continue
            except:
                pass
        
        print(f"✅ Fetched {len(internships)} SimplyHired internships")
        return internships
        
    except Exception as e:
        print(f"❌ SimplyHired request failed: {e}")
        return []

def fetch_naukri_internships():
    """Fetch internships from Naukri (Advanced Extraction)"""
    try:
        print("🔍 Fetching Naukri internships...")
        internships = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Method 1: Try main search
        urls_to_try = [
            "https://www.naukri.com/data-science-intern-jobs-in-india",
            "https://www.naukri.com/internship-jobs",
            "https://www.naukri.com/job-search?q=data+science+intern",
            "https://www.naukri.com/jobs?q=internship+data+science"
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try different selectors
                    selectors_to_try = [
                        'div.jobTuple',
                        'article.job',
                        'div.job-listing',
                        'div[class*="job"]',
                        'li.jobTuple',
                        'div.srp-jobtuple',
                        'a[href*="job"]'
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            if '[' in selector:
                                job_listings = soup.select(selector)
                            else:
                                job_listings = soup.find_all('div', class_=selector) or soup.find_all('article', class_=selector) or soup.find_all('li', class_=selector)
                            
                            if job_listings:
                                for listing in job_listings[:10]:
                                    try:
                                        # Extract title and link
                                        title_element = listing.find('a', class_='title') or listing.find('h2') or listing.find('a')
                                        if title_element:
                                            title = title_element.get_text().strip()
                                            href = title_element.get('href', '')
                                            if href.startswith('/'):
                                                link = 'https://www.naukri.com' + href
                                            elif href.startswith('http'):
                                                link = href
                                            else:
                                                continue
                                        else:
                                            continue
                                        
                                        # Extract company
                                        company_element = listing.find('span', class_='company') or listing.find('div', class_='company') or listing.find('span', class_='name')
                                        company = company_element.get_text().strip() if company_element else 'Unknown Company'
                                        
                                        # Extract location
                                        location_element = listing.find('span', class_='location') or listing.find('div', class_='location')
                                        location = location_element.get_text().strip() if location_element else 'Not specified'
                                        
                                        if ('intern' in title.lower() or 'internship' in title.lower()) and company != 'Unknown Company':
                                            internship = {
                                                'company': company,
                                                'role': title,
                                                'location': location,
                                                'link': link,
                                                'source': 'Naukri',
                                                'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            }
                                            internships.append(internship)
                                            print(f"  📋 {internship['role']} at {internship['company']}")
                                    except Exception as e:
                                        print(f"    ⚠️  Error processing Naukri listing: {e}")
                                        continue
                                
                                if len(internships) > 0:
                                    break
                        except:
                            continue
                            
                    if len(internships) > 0:
                        break
                        
            except:
                continue
        
        # Method 2: Try to find any internship mentions
        if len(internships) == 0:
            try:
                response = requests.get("https://www.naukri.com", headers=headers, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for any text containing 'intern'
                    elements = soup.find_all(text=re.compile(r'intern', re.IGNORECASE))
                    
                    for element in elements[:5]:
                        try:
                            parent = element.parent
                            if parent and parent.name == 'a':
                                title = parent.get_text().strip()
                                href = parent.get('href', '')
                                
                                if 'intern' in title.lower() and href:
                                    if href.startswith('http'):
                                        link = href
                                    elif href.startswith('/'):
                                        link = 'https://www.naukri.com' + href
                                    else:
                                        continue
                                    
                                    # Extract company
                                    company_match = re.search(r'at\s+([^\n|]+)', title, re.IGNORECASE)
                                    company = company_match.group(1).strip() if company_match else 'Indian Company'
                                    
                                    internship = {
                                        'company': company,
                                        'role': title,
                                        'location': 'India',
                                        'link': link,
                                        'source': 'Naukri',
                                        'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }
                                    internships.append(internship)
                                    print(f"  📋 {internship['role']} at {internship['company']}")
                        except Exception as e:
                            print(f"    ⚠️  Error processing Naukri element: {e}")
                            continue
            except:
                pass
        
        print(f"✅ Fetched {len(internships)} Naukri internships")
        return internships
        
    except Exception as e:
        print(f"❌ Naukri request failed: {e}")
        return []

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        bot_token = os.environ.get('BOT_TOKEN', '7954881918:AAEYS1vOaaG5CInjvTLCzohp0eFizePc8WQ')
        chat_id = os.environ.get('CHAT_ID', '6317336751')
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data, timeout=15)
        
        if response.status_code == 200:
            print("✅ Telegram message sent successfully")
            return True
        else:
            print(f"❌ Failed to send Telegram message: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def format_internships(internships):
    """Format internships for Telegram message"""
    if not internships:
        return "🔍 *No internships found*\n\nTry again later for new opportunities."
    
    message = "🌐 *ACIA Advanced Real Data Update*\n\n"
    
    # Group by source
    by_source = {}
    for internship in internships:
        source = internship.get('source', 'Unknown')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(internship)
    
    # Add summary
    message += f"📊 *Advanced Real Data Summary*\nTotal internships: {len(internships)}\n"
    for source, source_internships in by_source.items():
        message += f"• {source}: {len(source_internships)}\n"
    message += "\n"
    
    # Add internships by source
    for source, source_internships in by_source.items():
        message += f"🏢 *{source}*\n"
        
        for i, internship in enumerate(source_internships, 1):
            message += f"\n{i}. *{internship['role']}*\n"
            message += f"🏢 Company: {internship['company']}\n"
            message += f"📍 Location: {internship['location']}\n"
            message += f"🔗 [Apply]({internship['link']})\n"
    
    message += "\n🔍 *All data extracted using advanced methods*\n"
    message += "🤖 *Powered by ACIA on Render*"
    message += f"\n📅 *Advanced Real Data - {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
    
    return message

def run_acia_pipeline():
    """Run ACIA pipeline with advanced real data extraction"""
    try:
        logging.info("Starting ACIA Render pipeline - ADVANCED REAL DATA")
        print("🚀 ACIA Render Pipeline Started (Advanced Real Data)")
        print(f"Daily run at: {datetime.now()}")
        
        # Fetch internships from all 5 portals
        all_internships = []
        
        # Fetch from Stripe
        stripe_internships = fetch_stripe_internships()
        all_internships.extend(stripe_internships)
        time.sleep(2)
        
        # Fetch from LinkedIn
        linkedin_internships = fetch_linkedin_internships()
        all_internships.extend(linkedin_internships)
        time.sleep(2)
        
        # Fetch from Internshala
        internshala_internships = fetch_internshala_internships()
        all_internships.extend(internshala_internships)
        time.sleep(2)
        
        # Fetch from WeWorkRemotely
        wework_internships = fetch_weworkremotely_internships()
        all_internships.extend(wework_internships)
        time.sleep(2)
        
        # Fetch from SimplyHired
        simplyhired_internships = fetch_simplyhired_internships()
        all_internships.extend(simplyhired_internships)
        time.sleep(2)
        
        # Fetch from Naukri
        naukri_internships = fetch_naukri_internships()
        all_internships.extend(naukri_internships)
        
        if not all_internships:
            logging.warning("No real internships found")
            send_telegram_message("🔍 *No real internships found today*\n\nTry again tomorrow for new opportunities.")
            return False
        
        # Format and send to Telegram
        logging.info(f"Sending {len(all_internships)} advanced real internships to Telegram...")
        message = format_internships(all_internships)
        success = send_telegram_message(message)
        
        if success:
            logging.info("All advanced real internships sent successfully")
        else:
            logging.error("Failed to send advanced real internships")
        
        return success
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        return False

def main():
    """Main function for Render with advanced real data extraction"""
    # Setup logging
    setup_logging()
    
    try:
        # Run pipeline
        success = run_acia_pipeline()
        
        if success:
            logging.info("ACIA Render Run Completed Successfully (Advanced Real Data)")
            print("✅ ACIA Render Run Completed Successfully (Advanced Real Data)")
        else:
            logging.error("ACIA Render Run Failed")
            print("❌ ACIA Render Run Failed")
        
        return success
        
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        print(f"❌ Critical Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
