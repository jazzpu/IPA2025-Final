from ncclient import manager
import xmltodict
import json
import os

STUDENT_ID = os.getenv('STUDENT_ID') 
LOOPBACK_IP = "172.3.25.1" # IP ที่คำนวณได้จาก Student ID
LOOPBACK_ID = f"Loopback{STUDENT_ID}"
LOOPBACK_NETMASK = "255.255.255.0"

def netconf_edit_config(m, netconf_config):
    return  m.edit_config(target="running", config=netconf_config)

def create(ip_address):
    # ---!!! IPA2025: สร้าง Connection ภายในฟังก์ชัน
    with manager.connect(
        host=ip_address,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    ) as m:
    # ---!!!

        # สร้าง XML payload
        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
              <name>{LOOPBACK_ID}</name>
              <description>Configured by NETCONF</description>
              <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
              <enabled>true</enabled>
              <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                <address>
                  <ip>{LOOPBACK_IP}</ip>
                  <netmask>{LOOPBACK_NETMASK}</netmask>
                </address>
              </ipv4>
            </interface>
          </interfaces>
        </config>
        """

        try:
            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Hallelujah, You successfully created Interface {LOOPBACK_ID} ! (using netconfig)"
        except Exception as e:
            print(f"Error: {e}")
            return f"Error creating interface: {e} (using netconfig)"


def delete(ip_address):
    with manager.connect(
        host=ip_address, 
        port=830, 
        username="admin",
        password="cisco", 
        hostkey_verify=False
    ) as m:
        
        # XML payload สำหรับลบ (ใช้ operation="delete")
        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
              <name>{LOOPBACK_ID}</name>
            </interface>
          </interfaces>
        </config>
        """

        try:
            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Yay! successfully deleted Interface {LOOPBACK_ID} (using netconfig)"
        except Exception as e:
            print(f"Error: {e}")
            return f"Cannot delete: Interface {LOOPBACK_ID} (using netconfig)"
    netconf_config = """<!!!REPLACEME with YANG data!!!>"""

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "There are no errors inside xml from netconf"
    except:
        print("Error!")


def enable(ip_address):
    with manager.connect(
        host=ip_address, port=830, username="admin",
        password="cisco", hostkey_verify=False
    ) as m:

        # XML payload สำหรับ merge (แก้แค่ enabled)
        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
              <name>{LOOPBACK_ID}</name>
              <enabled>true</enabled>
            </interface>
          </interfaces>
        </config>
        """

        try:
            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Interface {LOOPBACK_ID} is enabled successfully :D (using netconfig)"
        except Exception as e:
            print(f"Error: {e}")
            return f"Cannot enable: Interface {LOOPBACK_ID} (using netconfig)"


def disable(ip_address):
    with manager.connect(
        host=ip_address, port=830, username="admin",
        password="cisco", hostkey_verify=False
    ) as m:

        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
              <name>{LOOPBACK_ID}</name>
              <enabled>false</enabled>
            </interface>
          </interfaces>
        </config>
        """

        try:
            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Interface {LOOPBACK_ID} is now down :P (using netconfig)"
        except Exception as e:
            print(f"Error: {e}")
            return f"Cannot shutdown: Interface {LOOPBACK_ID} (using netconfig)"

def status(ip_address):
    with manager.connect(
        host=ip_address, port=830, username="admin",
        password="cisco", hostkey_verify=False
    ) as m:
    
        # Filter XML สำหรับ <get> operational data (interfaces-state)
        netconf_filter = f"""
        <filter>
          <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces-state">
            <interface>
              <name>{LOOPBACK_ID}</name>
            </interface>
          </interfaces-state>
        </filter>
        """

        try:
            # ใช้ m.get()
            netconf_reply = m.get(filter=netconf_filter)
            print(netconf_reply)
            
            # ใช้ xmltodict.parse()
            netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

            # เช็คว่ามี data.interfaces-state.interface หรือไม่
            interface_data = netconf_reply_dict.get("data", {}).get("interfaces-state", {}).get("interface")

            if interface_data:
                # ตรวจสอบว่าได้ list หรือ dict
                if isinstance(interface_data, list):
                    # ถ้าเป็น list (อาจจะเกิดถ้า filter กว้างไป) ให้เอาตัวแรก
                    interface_data = interface_data[0]

                admin_status = interface_data.get("admin-status")
                oper_status = interface_data.get("oper-status")
                
                if admin_status == 'up' and oper_status == 'up':
                    return f"Interface {LOOPBACK_ID} is enabled (using netconfig)"
                elif admin_status == 'down' and oper_status == 'down':
                    return f"Interface {LOOPBACK_ID} is disabled (using netconfig)"
                else:
                    return f"Interface {LOOPBACK_ID} status is {admin_status}/{oper_status} (using netconfig)"
            else: # ไม่มี data
                return f"No Interface {LOOPBACK_ID} (using netconfig)"
        except Exception as e:
           print(f"Error: {e}")
           return f"Error checking status: {e} (using netconfig)"
        