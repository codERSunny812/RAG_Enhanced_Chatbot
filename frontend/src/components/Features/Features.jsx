import React from 'react';
import { Home, Car, HeartPulse, ShieldAlert } from 'lucide-react';
import './Features.css';

const services = [
  {
    title: 'Home Insurance',
    description: 'Comprehensive coverage for your most valuable asset, ensuring you are protected against unexpected damages.',
    icon: <Home size={40} className="service-icon" />
  },
  {
    title: 'Auto Insurance',
    description: 'Drive with confidence knowing you have premium protection against accidents and unforeseen events.',
    icon: <Car size={40} className="service-icon" />
  },
  {
    title: 'Health Insurance',
    description: 'Exceptional healthcare coverage to keep you and your family healthy without financial worry.',
    icon: <HeartPulse size={40} className="service-icon" />
  },
  {
    title: 'Life Insurance',
    description: 'Secure your family\'s financial future and leave a lasting legacy with our robust life policies.',
    icon: <ShieldAlert size={40} className="service-icon" />
  }
];

const Features = () => {
  return (
    <section id="features" className="features-section">
      <div className="container">
        <div className="section-header text-center">
          <h2 className="section-title">Comprehensive Coverage</h2>
          <p className="section-subtitle">Tailored protection plans to fit every aspect of your life.</p>
        </div>
        
        <div className="services-grid">
          {services.map((service, index) => (
            <div className="service-card" key={index}>
              <div className="icon-wrapper">
                {service.icon}
              </div>
              <h3 className="service-title">{service.title}</h3>
              <p className="service-desc">{service.description}</p>
              <a href="#" className="service-link">Learn More <span>&rarr;</span></a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
