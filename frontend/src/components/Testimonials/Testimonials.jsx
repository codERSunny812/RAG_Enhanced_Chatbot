import React from 'react';
import { Star } from 'lucide-react';
import './Testimonials.css';
import aditiyaImg from '../../assets/adi.png'
import subhImg from '../../assets/shubh.png'
import suchiImg from '../../assets/suchii.png'

const reviews = [
  {
    name: "Aditiya",
    role: "Homeowner",
    image: aditiyaImg,
    feedback: "Stellar  Insure provided me with excellent service and comprehensive coverage. I highly recommend them to anyone looking for reliable insurance solutions."
  },
  {
    name: "Subhadeep",
    role: "Business Owner",
    image: subhImg,
    feedback: "I've been a customer for years, and they have always been responsive and helpful whenever I've needed them. Great service and absolute peace of mind!"
  },
  {
    name: "Suchii",
    role: "Parent",
    image: suchiImg,
    feedback: "They helped me find the perfect life insurance plan tailored to my family's needs and budget. I couldn't be happier with their straightforward process."
  }
];

const Testimonials = () => {
  return (
    <section id="reviews" className="testimonials-section">
      <div className="container">
        <div className="section-header text-center">
          <h2 className="section-title">What Our Customers Say</h2>
          <p className="section-subtitle">Don't just take our word for it. Read reviews from people we've protected.</p>
        </div>
        
        <div className="testimonials-grid">
          {reviews.map((review, index) => (
            <div className="testimonial-card" key={index}>
              <div className="stars">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={18} fill="#FFC107" color="#FFC107" />
                ))}
              </div>
              <p className="testimonial-text">"{review.feedback}"</p>
              <div className="testimonial-author">
                <img src={review.image} alt={review.name} className="author-image" />
                <div className="author-info">
                  <h4 className="author-name">{review.name}</h4>
                  <span className="author-role">{review.role}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
